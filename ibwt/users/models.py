from flask_user import UserMixin
from ibwt.app_and_db import db
import datetime, base64, os
import onetimepass
import pytz

class AwareDateTime(db.TypeDecorator):
    '''Results returned as aware datetimes, not naive ones.
    '''

    impl = db.DateTime

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=pytz.utc)

# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)


    #oauth2 ids
    google_id = db.Column(db.String(255),default='',nullable=False)
    facebook_id = db.Column(db.String(255),default='',nullable=False)
    avatar = db.Column(db.String(255), nullable=False, default='')

    # User email information (required for Flask-User)
    email = db.Column(db.String(255), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.String(50), nullable=False, server_default='')
    last_name = db.Column(db.String(50), nullable=False, server_default='')

    # Relationships
    user_auth = db.relationship('UserAuth', uselist=False)
    roles = db.relationship('Role', secondary='user_roles',
            backref=db.backref('users', lazy='dynamic'))

    # currencies
    USD = db.Column(db.Numeric(14, 6), default=0)
    EUR = db.Column(db.Numeric(14, 6), default=0)
    RUR = db.Column(db.Numeric(14, 6), default=0)
    CNY = db.Column(db.Numeric(14, 6), default=0)
    JPY = db.Column(db.Numeric(14, 6), default=0)

    # cryptocurrencies
    BTC = db.Column(db.Numeric(14, 6), default=9999)
    LTC = db.Column(db.Numeric(14, 6), default=9999)
    QRK = db.Column(db.Numeric(14, 6), default=9999)
    NVC = db.Column(db.Numeric(14, 6), default=9999)
    NMC = db.Column(db.Numeric(14, 6), default=9999)
    NVC = db.Column(db.Numeric(14, 6), default=9999)
    XPM = db.Column(db.Numeric(14, 6), default=9999)
    BTC = db.Column(db.Numeric(14, 6), default=9999)
    DRK = db.Column(db.Numeric(14, 6), default=9999)
    PPC = db.Column(db.Numeric(14, 6), default=9999)
    PPC = db.Column(db.Numeric(14, 6), default=9999)
    URO = db.Column(db.Numeric(14, 6), default=9999)
    DOGE = db.Column(db.Numeric(14, 6), default=9999)

    locale = db.Column(db.String(50), nullable=False, default='en')
    timezone = db.Column(db.String(50), nullable=False, default='Europe/Amsterdam')

    # security
    white_list_ip = db.Column(db.Text(), nullable=False, default='')
    otp_secret = db.Column(db.String(16))

    # create and modifiy time
    created_date = db.Column(AwareDateTime, default=db.func.now(), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())


    def create_2fa(self):
        # generate a random secret
        otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')
        return otp_secret

    def delete_2fa(self):
        # generate a random secret
        self.otp_secret = ''

    def get_totp_uri(self):
        return 'otpauth://totp/%s?secret=%s&issuer=IBWT' % (self.email, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)


# Define the UserAuth data model.
class UserAuth(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))

    # User authentication information (required for Flask-User)
    username = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')

    # Relationships
    user = db.relationship('User', uselist=False)


# Define the Role data model
class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(255))


# Define the UserRoles association model
class UserRoles(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

class UserDepositWithdrawal(db.Model):
    # internal fields
    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String(32), nullable=False)
    transaction_type = db.Column(db.String(255),default='',nullable=False, index=True)
    id_user = db.Column(db.Integer(), index=True)
    provider = db.Column(db.String(255),default='',nullable=False)
    address = db.Column(db.String(255),default='',nullable=False)
    amount = db.Column(db.Numeric(14, 6), default=0)
    currency = db.Column(db.String(255),default='',nullable=False, index=True)
    status = db.Column(db.Integer(),default=1,nullable=False)
    # 1 - da esegure
    # > 2 - errore
    # eseguito

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
