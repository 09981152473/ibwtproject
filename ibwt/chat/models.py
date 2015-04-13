from ibwt.app_and_db import mdb

class Message(mdb.Document):
    text = mdb.StringField(verbose_name="Message", max_length=255, required=True)
    locale = mdb.StringField(verbose_name="Locale", max_length=255,)
    at = mdb.DateTimeField()
    user = mdb.StringField(verbose_name="User", max_length=255,required=True)
