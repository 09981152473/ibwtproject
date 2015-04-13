# -*- coding: utf-8 -*-

import os, locale
ADMINS = ['bigadsoleiman@gmail.com',]
#uDyDOFZchP2lc5OhFAUU
SECRET_KEY = 'uDyDOFZchP2lc5OhFAUUaGKpfIOQjVcUp|gvL00\qABKbM7L_mXcoLbzshX5HpjogtMKf6bkNghZAgX2EaufJtuAIXbVsW66L0Zuf7qnxtJy9IFNYLMMhpTZ07C'
SESSION_KEY_BITS = 2048
SESSION_COOKIE_NAME = 'bC1YIDQBsG'
DEBUG = False
DEBUG_TB_ENABLED = False
DEBUG_TB_PROFILER_ENABLED = False
DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
DEBUG_TB_INTERCEPT_REDIRECTS = False
WTF_CSRF_ENABLED = True
CSRF_ENABLED = True
WTF_CSRF_SSL_STRICT = True
SESSION_COOKIE_SECURE = True
PREFERRED_URL_SCHEME = 'https'


# DB SETTINGS
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://web:klNLwLlMJhk5ItUiMZGH@localhost/ibwt'
MONGODB_SETTINGS = {'DB': "ibwt_chat"}


# MAIL SETTINGS
MAIL_DEFAULT_SENDER = '"IBWT" <accounts@inbitwetrust.com>'
MAIL_SERVER = 'localhost'
MAIL_PORT=25
USER_APP_NAME = 'IBWT'
USER_ENABLE_CONFIRM_EMAIL = True
USER_ENABLE_USERNAME        = False              # Register and Login with username
USER_ENABLE_CHANGE_USERNAME = False
MAIL_USE_TLS = False

# Email template files                  # Defaults
USER_CONFIRM_EMAIL_EMAIL_TEMPLATE       = 'flask_user/emails/confirm_email'
USER_FORGOT_PASSWORD_EMAIL_TEMPLATE     = 'flask_user/emails/forgot_password'
USER_PASSWORD_CHANGED_EMAIL_TEMPLATE    = 'flask_user/emails/password_changed'
USER_REGISTERED_EMAIL_TEMPLATE          = 'flask_user/emails/registered'
USER_USERNAME_CHANGED_EMAIL_TEMPLATE    = 'flask_user/emails/username_changed'

DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        # Add the line profiling
        'flask_debugtoolbar_lineprofilerpanel.panels.LineProfilerPanel'
    ]

BABEL_DEFAULT_LOCALE = 'en'

LANGUAGES = {
#    'bg': 'Bulgarian',
#    'cs': 'Czech',
#    'da': 'Danish',
    'de': 'German',
#    'el': 'Greek',
    'en': 'English',
    'es': 'Spanish',
#    'et': 'Estonian',
#    'fi': 'Finnish',
    'fr': 'French',
#    'hr': 'Croatian',
#    'hu': 'Hungarian',
    'it': 'Italian',
#    'lt': 'Lithuanian',
#    'lv': 'Latvian',
#    'nl': 'Dutch',
#    'no': 'Norwegian',
#    'pl': 'Polish',
#    'pt': 'Portuguese',
#    'ro': 'Romanian',
    'ru': 'Russian',
#    'sk': 'Slovak',
#    'sl': 'Slovenian',
#    'sv': 'Swedish',
#    'tr': 'Turkish',
    'ja': 'Japanese',
    'zh': 'Chinese',
}



# sijax
path = os.path.join('.', os.path.dirname(__file__), 'static/js/sijax/')
SIJAX_STATIC_PATH = path
SIJAX_JSON_URI = '/static/js/sijax/json2.js'

# Place the Login form and the Register form on one page:
# Only works for Flask-User v0.4.9 and up
USER_LOGIN_TEMPLATE                     = 'flask_user/login.html'
USER_REGISTER_TEMPLATE                  = 'flask_user/login.html'


# oAuth google
GOOGLE_LOGIN_CLIENT_ID = '308375231537-cdph13pu0u5apm1ncl22rnb61kvuvci9.apps.googleusercontent.com'
GOOGLE_LOGIN_CLIENT_SECRET = 'PRhVwbodKw7DP3UJh25rss5C'
GOOGLE_LOGIN_REDIRECT_URI =  '/login/google'
GOOGLE_LOGIN_REDIRECT_SCHEME = 'https'

# oAuth facebook
FACEBOOK_APP_ID = '288115984721576'
FACEBOOK_APP_SECRET = '70cd2d3e79bf6083e5740fb992392c9b'
