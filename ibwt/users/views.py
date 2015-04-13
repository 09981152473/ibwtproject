from io import StringIO
import uuid

import pyqrcode
from flask import redirect, render_template, \
    session, flash
from flask_babel import gettext as _
from flask import request, url_for
from flask_user import current_user, login_required
from flask.ext.babel import refresh
from flask_oauth import OAuth
from babel import Locale
import requests

from ibwt.startup import settings
from ibwt.app_and_db import app, db, db_adapter
from ibwt.users.models import User, UserDepositWithdrawal
from ibwt.users.forms import UserProfileForm, UserWithdrawalForm, UserOTPLoginForm
from ibwt.orders.models import Transaction, UserWallet
from ibwt.startup.wallets_settings import *
from ibwt.startup.settings import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET, GOOGLE_LOGIN_CLIENT_ID, \
    GOOGLE_LOGIN_CLIENT_SECRET


oauth = OAuth()

# FACEBOOK
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope':'email'}
)

google = oauth.remote_app('google',
  base_url='https://www.google.com/accounts/',
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  request_token_url=None,
  request_token_params= {'scope': 'https://www.googleapis.com/auth/userinfo.email \
  https://www.googleapis.com/auth/userinfo.profile',
                         'response_type': 'code'},
  access_token_url='https://accounts.google.com/o/oauth2/token',
  access_token_method='POST',
  access_token_params={'grant_type': 'authorization_code'},
  consumer_key=GOOGLE_LOGIN_CLIENT_ID,
  consumer_secret=GOOGLE_LOGIN_CLIENT_SECRET)


# User Profile form
#
@app.route('/user/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    return render_template('users/user_profile_page.html')

@app.route('/user/account', methods=['GET', 'POST'])
@login_required
def user_account_page():
    # Initialize form
    form = UserProfileForm(request.form, current_user)

    # Process valid POST
    if request.method=='POST' and form.validate():

        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # set default locale
        if session.get('language', settings.BABEL_DEFAULT_LOCALE) != current_user.locale:
            session['language'] = current_user.locale
            l = Locale.parse( session['language'])
            refresh()
            flash(_('Your language has been set to: %s'% l.language_name))

        # Redirect to home page
        return redirect(url_for('user_account_page') )

    # Process GET or invalid POST
    return render_template('users/user_account_page.html',
                           form=form)

@app.route('/user/orders/open/buy', methods=['GET',])
@login_required
def user_buy_orders_page():
    return render_template('users/user_buy_orders_page.html')


@app.route('/user/orders/open/sell', methods=['GET',])
@login_required
def user_sell_orders_page():
    return render_template('users/user_sell_orders_page.html')

@app.route('/user/orders/open', methods=['GET',])
@login_required
def user_orders_page():
    return render_template('users/user_orders_page.html')


@app.route('/user/orders/closed', methods=['GET',])
@login_required
def user_orders_closed_page():
    return render_template('users/user_orders_closed_page.html')

@app.route('/user/orders/closed/buy', methods=['GET',])
@login_required
def user_buy_orders_closed_page():
    return render_template('users/user_buy_orders_closed_page.html')


@app.route('/user/orders/closed/sell', methods=['GET',])
@login_required
def user_sell_orders_closed_page():
    return render_template('users/user_sell_orders_closed_page.html')

@app.route('/user/transactions', methods=['GET',])
@login_required
def user_transactions_page():
    return render_template('users/user_transactions_page.html')


@app.route('/user/transactions/accredit', methods=['GET',])
@login_required
def user_transactions_accredit_page():
    return render_template('users/user_transactions_accredit_page.html')

@app.route('/user/transactions/charge', methods=['GET',])
@login_required
def user_transactions_charge_page():
    return render_template('users/user_transactions_charge_page.html')

@app.route('/user/deposit-withdrawals', methods=['GET',])
@login_required
def user_deposits_withdrawals_page():
    return render_template('users/user_deposits_withdrawals_page.html')

@app.route('/user/deposit', methods=['GET',])
@login_required
def user_deposits_page():
    return render_template('users/user_deposits_page.html')

@app.route('/user/withdrawals', methods=['GET',])
@login_required
def user_withdrawals_page():
    return render_template('users/user_withdrawals_page.html')


@app.route('/user/funds', methods=['GET',])
@login_required
def user_funds_page():
    # Process GET or invalid POST
    return render_template('users/user_funds_page.html')


@app.route('/user/funds/withdrawal/<currency>', methods=['GET','POST'])
@login_required
def user_funds_withdrawal_page(currency):
    # Process GET or invalid POST
    # Initialize form
    form = UserWithdrawalForm(request.form)

    # Process valid POST
    if request.method=='POST' and form.validate():
        current_user_amount = getattr(current_user, form.currency.data)
        address = form.address.data
        amount_to_withdraw =  form.amount.data
        if current_user_amount >= amount_to_withdraw:

            new_user_amount = current_user_amount - amount_to_withdraw

            # remove from user wallet
            user_upd = db_adapter.find_first_object(User, id=current_user.id)
            db_adapter.update_object(user_upd,**{form.currency.data: new_user_amount})

            # set transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(UserDepositWithdrawal,
                                  uuid = tid,
                                  id_user = current_user.id,
                                  currency = currency,
                                  amount=amount_to_withdraw,
                                  provider='user',
                                  address=address,
                                  transaction_type='withdrawal',
                                  status=1)
            db_adapter.commit()
            flash(_('All right, your withdrawal request of %s %s will be processed soon.' % (amount_to_withdraw, currency) ), 'success')
            redirect(url_for('user_funds_page'))
        else:
            flash(_('Sorry, insufficient funds (%s) to withdraw %s %s' % (current_user_amount, amount_to_withdraw, currency) ), 'error')


    return render_template('users/user_funds_withdrawal_page.html',
                           currency=currency,
                           form=form)


@app.route('/user/funds/transactions/<currency>')
@login_required
def funds_transaction_page(currency):
    transactions = db_adapter.find_all_objects(Transaction,
                                               id_user=current_user.id,
                                               currency=currency)
    return render_template('flask_user/funds_transaction.html',
                           transactions=transactions,
                           currency=currency)

# ALTCOIN
@app.route('/user/funds/deposit/<currency>')
@login_required
def funds_crypto_load(currency):
    user_wallet = db_adapter.find_first_object(UserWallet,
                                               id_user=current_user.id,
                                               currency=currency)
    if not user_wallet:
        try:
            generate_new_address(currency)
        except Exception, e:
            user_wallet = {'address': _('Wallet not avaiable at the moment')}
            flash(_('Connection problem with your wallet please try again in a minute') + ' -  ' + repr(e), 'error')
    user_wallet = db_adapter.find_first_object(UserWallet, id_user=current_user.id,
                                               currency=currency)

    return render_template('users/user_funds_crypto.html',
                       currency=currency,
                       user_wallet=user_wallet)


@app.route('/user/funds/new-address/<currency>')
@login_required
def funds_crypto_new_address(currency):
    user_wallet = db_adapter.find_first_object(UserWallet,
                                               id_user=current_user.id,
                                               currency=currency)
    if not user_wallet or user_wallet.flag_used:
        generate_new_address(currency)
    return redirect(url_for('funds_crypto_load', currency=currency))


def generate_new_address(currency):
    user_wallet = db_adapter.find_first_object(UserWallet,
                                               id_user=current_user.id,
                                               currency=currency)
    if user_wallet and not user_wallet.flag_used:
        return user_wallet.address

    if currency == 'BTC':
        new_address = btc_client.call("getnewaddress", BTC_ACCOUNT)
    elif currency == 'LTC':
        new_address = ltc_client.call("getnewaddress", LTC_ACCOUNT)
    elif currency == 'QRK':
        new_address = qrk_client.call("getnewaddress", QRK_ACCOUNT)
    elif currency == 'PPC':
        new_address = ppc_client.call("getnewaddress", PPC_ACCOUNT)
    elif currency == 'NMC':
        new_address = nmc_client.call("getnewaddress", NMC_ACCOUNT)
    elif currency == 'NVC':
        new_address = nvc_client.call("getnewaddress", NVC_ACCOUNT)
    elif currency == 'DRK':
        new_address = drk_client.call("getnewaddress", DRK_ACCOUNT)
    else:
        new_address = 'n/d'
    if new_address != 'n/d':
        if not user_wallet:
            db_adapter.add_object(UserWallet,
                                  id_user=current_user.id,
                                  currency=currency,
                                  address=new_address)
        else:
            db_adapter.update_object(user_wallet,
                                     address=new_address,
                                     flag_used=0)
        db_adapter.commit()
    return new_address



@app.route('/oauth/facebook')
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/oauth/login/google')
def google_login():
    return google.authorize(callback=url_for('google_authorized',
                                             _external=True))


@app.route('/oauth/facebook/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        flash('Facebook authentication denied. Please consider register with IBWT', 'error')
        flash('Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        ), 'error')
        return redirect(url_for('home_page'))

    session['oauth_token'] = (resp['access_token'], '')
    resp = facebook.get('/me')
    profile = resp.data

    profile_fields_required = ['id',]
    for field_req in profile_fields_required:
            if not profile.get(field_req,False):
                flash('Login failed due to a Facebook problem. Please consider to register with IBWT', 'error')
                return redirect(url_for('auth.register'))

    user = db_adapter.find_first_object(User, facebook_id=profile['id'])
    if user:
        login_user(user)
    else:
        if profile.get('email','') != '':
            user = db_adapter.find_first_object(User, email=profile['email'])
            if user:
                db_adapter.update_object(user, facebook_id=profile['id'])
                db_adapter.commit()
                login_user(user)
                flash('Account connected to Facebook', 'success')
                return redirect(url_for('auth.profile_page'))
        user = db_adapter.add_object(User,
                    name=profile.get('name',''),
                    facebook_id=profile.get('id',''),
                    avatar=profile.get('picture',''),
                    email=profile.get('email',''),
                    active=1,
                    usd=1000,
                    eur=1500,
                    btc=500)
        db_adapter.commit()
        login_user(user)
        flash('Account created from Facebook', 'success')
    return redirect(url_for('auth.profile_page'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')



# GOOGLE
@app.route('/oauth/google/authorized')
@google.authorized_handler
def google_authorized(resp):
    if not resp:
        flash('Google authentication denied. Please consider register with IBWT', 'error')
        return redirect(url_for('user.register'))

    access_token = resp['access_token']
    profile = {}
    session['access_token'] = access_token, ''
    if access_token:
        r = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                         headers={'Authorization': 'OAuth ' + access_token})
        if r.ok:
            profile = json.loads(r.text)
        profile_fields_required = ['id',]
        for field_req in profile_fields_required:
                if not profile.get(field_req,False):
                    flash('Login failed due to a Google problem. Please consider to register with IBWT', 'error')
                    return redirect(url_for('auth.register'))

        user = db_adapter.find_first_object(User, google_id=profile['id'])
        if user:
            login_user(user)
        else:
            if profile.get('email','') != '':
                userE = db_adapter.find_first_object(User, email=profile['email'])
                if userE:
                    db_adapter.update_object(userE, google_id=profile.get('id',''))

                    db_adapter.commit()
                    login_user(userE)
                    flash('Account connected to Google', 'success')
                    return redirect(url_for('auth.profile_page'))
            user = db_adapter.add_object(User,
                        name=profile.get('name',''),
                        google_id=profile.get('id',''),
                        avatar=profile.get('picture',''),
                        email=profile.get('email',''),
                        active=1,
                        USD=1000,
                        EUR=1500,
                        RUR=1000,
                        CNY=1500,
                        JPY=1000,
                        BTC=1500,
                        DOGE=1500,
                        LTC=1500,
                        NVC=1500,
                        XPM=1500)
            db_adapter.commit()
            login_user(user)
            flash('Account created from Google','success')
        return redirect(url_for('user_profile_page'))
    else:
        flash('Google authentication due to a Google service problem. Please consider register with IBWT', 'error')
        return redirect(url_for('home_page'))

@google.tokengetter
def get_access_token():
    return session.get('access_token')


@app.route('/user/security', methods=['GET',])
@login_required
def user_security_page():
    return render_template('users/user_security_page.html')



# TWO FACTOR AUTH
@app.route('/twofactor/register', methods=['GET', 'POST'])
def twofactor_register():
    """User registration route."""
    if current_user.is_authenticated():
        # if user is logged in we get out of here
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('Username already exists.')
            return redirect(url_for('register'))
        # add new user to the database
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()

        # redirect to the two-factor auth page, passing username in session
        session['username'] = user.username
        return redirect(url_for('two_factor_setup'))
    return render_template('register.html', form=form)


@app.route('/twofactor')
def two_factor_setup():
    if not current_user.is_authenticated():
        return redirect(url_for('home_page'))
    if current_user is None:
        return redirect(url_for('home_page'))
    # since this page contains the sensitive qrcode, make sure the browser
    # does not cache it
    return render_template('users/two-factor-setup.html'), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/twofactor/qrcode')
def two_factor_qrcode():
    if not current_user.is_authenticated():
        abort(404)
    if current_user is None:
        abort(404)


    if not current_user.otp_secret:
        session['2FA'] = True
        user = db_adapter.find_first_object(User, id=current_user.id)
        db_adapter.update_object(user, otp_secret = current_user.create_2fa())
        db_adapter.commit()
    # render qrcode for FreeTOTP

    url = pyqrcode.create(current_user.get_totp_uri())
    stream = StringIO()
    url.svg(stream, scale=3)
    return stream.getvalue().encode('utf-8'), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@app.route('/twofactor/login', methods=['GET', 'POST'])
@login_required
def two_factor_login():
    """User login route."""
    two_factor_form = UserOTPLoginForm()
    if two_factor_form.validate_on_submit():
        if not current_user.verify_totp(two_factor_form.otp_code.data):
            flash('Invalid one time password please try again.', 'error')
            return redirect(url_for('two_factor_login'))
        # log user in
        session['2FA'] = True
        return redirect(url_for('user_profile_page'))
    return render_template('users/user_otp_login.html',
                           two_factor_form=two_factor_form)



@app.route('/user/security/no-two-factor', methods=['GET',])
@login_required
def user_security_no_two_factor():
    user = db_adapter.find_first_object(User, id=current_user.id)
    db_adapter.update_object(user,
                             otp_secret = '')
    db_adapter.commit()
    return redirect(url_for('user_security_page'))

