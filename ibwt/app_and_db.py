import os
import json
import hmac
import random
import decimal
import pytz
import isodate
import redis
import babel as native_babel
import flask_sijax

from string import ascii_letters, digits
from hashlib import sha1
from datetime import date
from urlparse import urlparse, urljoin

from flask import Flask, flash, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.babel import Babel
from flask_user import current_user, SQLAlchemyAdapter
from flask import g, redirect, session
from flask.ext.qrcode import QRcode
from flask_kvsession import KVSessionExtension
from simplekv.memory.redisstore import RedisStore
from flask.ext.socketio import SocketIO
from flask.ext.assets import Environment
from flask_wtf.csrf import CsrfProtect
from flask.ext.babel import format_datetime
from babel.numbers import format_decimal as format_number
from flask.ext.mongoengine import MongoEngine
from flask_babel import gettext as _


from startup.settings import LANGUAGES, BABEL_DEFAULT_LOCALE
from startup.currencies_settings import EXCHANGABLE_CURRENCIES


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
    }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
       if hasattr(obj, 'isoformat'):
           return obj.isoformat()
       elif isinstance(obj, decimal.Decimal):
           return float(obj)
       elif isinstance(obj, ModelState):
           return None
       else:
           return json.JSONEncoder.default(self, obj)

store = RedisStore(redis.StrictRedis())

# This is the WSGI compliant web application object
app = Flask(__name__)
app.config.from_object('ibwt.startup.settings')          # Read config from 'ibwt/startup/settings.py' file
app.config.from_object('ibwt.startup.wallets_settings') # Read config from 'ibwt/startup/settings.py' file
app.config.from_object('ibwt.startup.currencies_settings') # Read config from 'ibwt/startup/settings.py' file
app.wsgi_app = ReverseProxied(app.wsgi_app)
KVSessionExtension(store, app)
socketio = SocketIO(app)
CsrfProtect(app)
QRcode(app)
babel = Babel(app)
flask_sijax.Sijax(app)
assets = Environment(app)

# This is the SQLAlchemy ORM object
db = SQLAlchemy(app)
db_adapter = SQLAlchemyAdapter(db, None)
mdb = MongoEngine(app)


@app.template_global('csrf_token')
def csrf_token():
    """
    Generate a token string from bytes arrays. The token in the session is user
    specific.
    """
    if "_csrf_token" not in session:
        session["_csrf_token"] = os.urandom(128)
    return hmac.new(app.secret_key, session["_csrf_token"],
            digestmod=sha1).hexdigest()


@babel.localeselector
def get_locale():
    if 'language' in session:
        if session['language']:
            session['language'] = session['language'].lower()
            if session['language'] in LANGUAGES.keys():
                return session['language']
    # if a user is logged in, use the locale from the user settings
    if current_user is not None and current_user.is_authenticated():
        session['language'] = current_user.locale.lower()
        return current_user.locale.lower()
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    session['language'] = request.accept_languages.best_match(LANGUAGES.keys())
    if not session['language']:
        session['language'] = 'en'
    return session['language']


@babel.timezoneselector
def get_timezone():
    if current_user is not None and current_user.is_authenticated():
        return current_user.timezone
    else:
        return 'Europe/Amsterdam'


@app.route('/lang/<language>')
def lang(language=None):
    language = language.strip().lower()
    if not language or \
        language not in LANGUAGES:
            language = BABEL_DEFAULT_LOCALE
    session['language'] = language
    return redirect(url_for('home_page'))

@app.route('/trade/<currency>/<currency2>')
def trade(currency, currency2):
    if currency == currency2:
        flash('Cannot exchange with same currency', 'error')
    elif (currency, currency2) in EXCHANGABLE_CURRENCIES:
        session['currencies'] = (currency, currency2)
    else:
        flash('Exchange %s with %s is unavaiable' %(currency, currency2), 'error')
    return redirect(url_for('home_page'))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target

def redirect_back(endpoint='back', **values):
    if endpoint == 'back':
        target = request.referrer
    else:
        target = request.form['next']
        if target == 'back':
            target = request.referrer
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


@app.before_request
def before_request():
    g.languages = LANGUAGES
    g.site_currencies = app.config['SITE_CURRENCIES']
    g.crypto_currencies = app.config['CRYPTO_CURRENCIES']
    g.paypal_currencies = app.config['PAYPAL_CURRENCIES']
    g.bank_currencies = app.config['BANK_CURRENCIES']
    g.top_currencies = app.config['TOP_CURRENCIES']
    g.exchangable_currencies = app.config['EXCHANGABLE_CURRENCIES']
    g.fee_per_currency = app.config['FEE_PER_CURRENCIES']
    g.locale = get_locale()
    g.timezone = get_timezone()
    g.current_user = current_user
    g.year = date.today().year

    if not 'currencies' in session:
        session['currencies'] = app.config['DEFAULT_EXCHANGABLE_CURRENCIES']
    g.currency = session['currencies'][0]
    g.currency2 = session['currencies'][1]

    if current_user.is_authenticated():
        if not session.get('2FA', False) and \
                current_user.otp_secret and \
                request.url_rule.endpoint not in ('two_factor_login', 'lang', 'user.logout'):
            # requested one-time password
            flash(_('Please type one time password to access your account'), 'warning')
            return redirect(url_for('two_factor_login'))
    else:
        if '2FA' in session:
            del session['2FA']


def generate_form_token():
    """Sets a token to prevent double posts."""
    if '_form_token' not in session:
        form_token = \
            ''.join([random.choice(ascii_letters+digits) for i in range(128)])
        session['_form_token'] = form_token
    return session['_form_token']


app.jinja_env.globals['form_token'] = generate_form_token

@app.template_filter()
def get_english_locale_name(value):
    l = native_babel.Locale.parse(value)
    return l.get_language_name('en')

@app.template_filter()
def convert_datetime(value):
    return format_datetime(value)

@app.template_filter()
def format_locale_number(value):
    return format_number(value,
                         locale=get_locale() or 'en')

@app.template_filter()
def iso_format(value):
    local_tz = get_timezone()
    return isodate.datetime_isoformat(value.replace(tzinfo=pytz.timezone(local_tz)))

