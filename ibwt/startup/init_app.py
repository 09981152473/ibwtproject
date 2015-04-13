import logging
from logging.handlers import SMTPHandler
from flask_mail import Mail
from flask_user import UserManager, SQLAlchemyAdapter, LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile
from logging.handlers import RotatingFileHandler
from flask.ext.mongoengine import MongoEngine

def init_app(app, db, extra_config_settings={}):
    """
    Initialize Flask applicaton
    """

    # Initialize ibwt config settings



    if app.testing:
        app.config['WTF_CSRF_ENABLED'] = False              # Disable CSRF checks while testing

    # Setup Flask-Mail
    mail = Mail(app)

    # Setup an error-logger to send emails to ibwt.config.ADMINS
    init_error_logger_with_email_handler(app)

    # Setup Flask-User to handle user account related forms
    from ibwt.users.models import UserAuth, User
    from ibwt.users.forms import MyRegisterForm
    from ibwt.users.views import user_profile_page
    db_adapter = SQLAlchemyAdapter(db, User,        # Setup the SQLAlchemy DB Adapter
            UserAuthClass=UserAuth)                 #   using separated UserAuth/User data models
    user_manager = UserManager(db_adapter, app,     # Init Flask-User and bind to ibwt
#            register_form=MyRegisterForm,           #   using a custom register form with UserProfile fields
            user_profile_view_function = user_profile_page,
            )

    # Load all models.py files to register db.Models with SQLAlchemy
    from ibwt.users import models

    # Load all views.py files to register @ibwt.routes() with Flask
    from ibwt.pages import views
    from ibwt.users import views
    from ibwt.orders import views
    from ibwt.chat import views

    return app


def init_error_logger_with_email_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to ibwt.config.ADMINS.
    """
    if app.debug: return                        # Do not send error emails while developing

    # Retrieve email settings from ibwt.config
    host      = app.config['MAIL_SERVER']
    port      = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve ibwt settings from ibwt.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    mail_handler = SMTPHandler(
        mailhost=(host, port),                  # Mail host and port
        fromaddr=from_addr,                     # From address
        toaddrs=to_addr_list,                   # To address
        subject=subject,                        # Subject line
       # credentials=(username, password),       # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

    # Log errors using: ibwt.logger.error('Some error message')

