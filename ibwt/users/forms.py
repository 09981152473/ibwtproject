from flask_user.forms import RegisterForm
from flask_wtf import Form
from ibwt.startup import settings
from wtforms import StringField, SubmitField, \
    validators, SelectField, DecimalField
from flask_babel import gettext as _
import pytz


# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])


# Define the User profile form
class UserProfileForm(Form):
    first_name = StringField(_('First name'), validators=[
        validators.DataRequired(_('First name is required'))])
    last_name = StringField(_('Last name'), validators=[
        validators.DataRequired(_('Last name is required'))])
    locale = SelectField(_('Preferred language'),
                         choices=[(x, settings.LANGUAGES[x]) for x in settings.LANGUAGES],)

    timezone = SelectField(_('Timezone'),
                           choices=[(x, x) for x in pytz.all_timezones])


    submit = SubmitField(_('Save'))

# Define the User profile form
class UserWithdrawalForm(Form):
    currency =  StringField(_('From'))
    amount = DecimalField(_('Amount'),
                          [validators.DataRequired(_('This field is required')),])

    address = StringField(_('Address'), validators=[
        validators.DataRequired(_('Address is required'))])


    submit = SubmitField(_('Save'))

# Define the User profile form
class UserOTPLoginForm(Form):
    otp_code = DecimalField(_(''),
                            [validators.DataRequired(_('This field is required and must be a number')),])

    submit = SubmitField(_('Login'))
