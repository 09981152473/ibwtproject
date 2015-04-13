# Import Form and RecaptchaField (optional)
from flask.ext.wtf import Form # , RecaptchaField
from flask_wtf import Form, RecaptchaField
from flask.ext.babel import gettext as _

# Import Form validators
from wtforms import Form, BooleanField,\
    TextField, PasswordField, validators, SelectField, DecimalField, StringField

import config

class BuyForm(Form):
    currency =  StringField(_('From'))
    currency2 =  StringField(_('To'))

    amount = DecimalField(_('Amount'),
                            [validators.DataRequired(_('This field is required')),
                             ])

    price_per_unit = DecimalField(_('Price'),
                            [validators.DataRequired(_('This field is required')),
                             ])



class SellForm(Form):
    currency =  StringField(_('From'))
    currency2 =  StringField(_('To'))

    amount = DecimalField(_('Amount'),
                            [validators.DataRequired(_('This field is required')),])
    price_per_unit = DecimalField(_('Price'),
                            [validators.DataRequired(_('This field is required')),])
