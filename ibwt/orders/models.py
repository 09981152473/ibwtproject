from ibwt.app_and_db import db
import datetime, uuid
import pytz

class AwareDateTime(db.TypeDecorator):
    '''Results returned as aware datetimes, not naive ones.
    '''

    impl = db.DateTime

    def process_result_value(self, value, dialect):
        return value.replace(tzinfo=pytz.utc)



class Buy(db.Model):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), default=uuid.uuid4().hex)
    uid = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    order_type = db.Column(db.String(10), default='buy')
    currency = db.Column(db.String(10),default='',nullable=False, index=True)
    currency2 = db.Column(db.String(10),default='',nullable=False, index=True)
    amount_start_no_fee = db.Column(db.Numeric(14, 6), default=0)
    amount_start = db.Column(db.Numeric(14, 6), default=0)
    amount = db.Column(db.Numeric(14, 6), default=0)
    diff = db.Column(db.Numeric(14, 6), default=0)
    initial_fee = db.Column(db.Numeric(14, 6), default=0)
    fee = db.Column(db.Numeric(14, 6), default=0)
    fee_percentage = db.Column(db.Numeric(14, 6), default=0)
    price_per_unit = db.Column(db.Numeric(14, 6), default=0)
    total_order = db.Column(db.Numeric(14, 6), default=0)
    total_order_no_fee = db.Column(db.Numeric(14, 6), default=0)
    flag_completed = db.Column(db.Integer(), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Sell %r>' % (self.uid)


class Sell(db.Model):

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), default=uuid.uuid4().hex)
    uid = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    order_type = db.Column(db.String(10), default='sell')
    currency = db.Column(db.String(10),default='',nullable=False, index=True)
    currency2 = db.Column(db.String(10),default='',nullable=False, index=True)
    amount_start_no_fee = db.Column(db.Numeric(14, 6), default=0)
    amount_start = db.Column(db.Numeric(14, 6), default=0)
    amount = db.Column(db.Numeric(14, 6), default=0)
    initial_fee = db.Column(db.Numeric(14, 6), default=0)
    fee = db.Column(db.Numeric(14, 6), default=0)
    fee_percentage = db.Column(db.Numeric(14, 6), default=0)
    price_per_unit = db.Column(db.Numeric(14, 6), default=0)
    total_order = db.Column(db.Numeric(14, 6), default=0)
    total_order_no_fee = db.Column(db.Numeric(14, 6), default=0)
    flag_completed = db.Column(db.Integer(), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Sell %r>' % (self.uid)

class SellBuy(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    order_type = db.Column(db.String(10), default='sell')
    usid = db.Column(db.Integer(), nullable=False)
    ubid = db.Column(db.Integer(), nullable=False)
    sid = db.Column(db.String(32),default='',nullable=False)
    bid = db.Column(db.String(32),default='',nullable=False)
    currency = db.Column(db.String(10),default='',nullable=False)
    currency2 = db.Column(db.String(10),default='',nullable=False)
    amount_of_buy = db.Column(db.DECIMAL(), default=0)
    price_per_unit = db.Column(db.DECIMAL(), default=0)
    price_per_unit_sell = db.Column(db.DECIMAL(), default=0)
    total_order = db.Column(db.DECIMAL(), default=0)
    total_order_sell = db.Column(db.DECIMAL(), default=0)
    total_order_no_fee = db.Column(db.DECIMAL(), default=0)
    diff = db.Column(db.DECIMAL(), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<BuySell %r>' % (self.id)

class BuyHistory(db.Model):

    id_history = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), nullable=False)
    uid = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    order_type = db.Column(db.String(10), default='buy')
    currency = db.Column(db.String(10),default='',nullable=False, index=True)
    currency2 = db.Column(db.String(10),default='',nullable=False, index=True)
    amount_start_no_fee = db.Column(db.Numeric(14, 6), default=0)
    amount_start = db.Column(db.Numeric(14, 6), default=0)
    amount = db.Column(db.Numeric(14, 6), default=0)
    diff = db.Column(db.Numeric(14, 6), default=0)
    initial_fee = db.Column(db.Numeric(14, 6), default=0)
    fee = db.Column(db.Numeric(14, 6), default=0)
    fee_percentage = db.Column(db.Numeric(14, 6), default=0)
    price_per_unit = db.Column(db.Numeric(14, 6), default=0)
    total_order = db.Column(db.Numeric(14, 6), default=0)
    total_order_no_fee = db.Column(db.Numeric(14, 6), default=0)
    flag_completed = db.Column(db.Integer(), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Buy %r>' % (self.uid)

class SellHistory(db.Model):

    id_history = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    uuid = db.Column(db.String(32), nullable=False)
    order_type = db.Column(db.String(10), default='sell')
    uid = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    currency = db.Column(db.String(10),default='',nullable=False, index=True)
    currency2 = db.Column(db.String(10),default='',nullable=False, index=True)
    amount_start_no_fee = db.Column(db.Numeric(14, 6), default=0)
    amount_start = db.Column(db.Numeric(14, 6), default=0)
    amount = db.Column(db.Numeric(14, 6), default=0)
    initial_fee = db.Column(db.Numeric(14, 6), default=0)
    fee = db.Column(db.Numeric(14, 6), default=0)
    fee_percentage = db.Column(db.Numeric(14, 6), default=0)
    price_per_unit = db.Column(db.Numeric(14, 6), default=0)
    total_order = db.Column(db.Numeric(14, 6), default=0)
    total_order_no_fee = db.Column(db.Numeric(14, 6), default=0)
    flag_completed = db.Column(db.Integer(), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Sell %r>' % (self.uid)



class TradeData(db.Model):
    # internal fields
    id = db.Column(db.Integer(), primary_key=True)
    currency = db.Column(db.String(255),default='',nullable=False, index=True)
    currency2 = db.Column(db.String(255),default='',nullable=False, index=True)
    min_buy_price = db.Column(db.Numeric(14, 6), default=0)
    max_sell_price = db.Column(db.Numeric(14, 6), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Transaction %r>' % (self.currency)


class Transaction(db.Model):
    # internal fields
    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String(32), nullable=False)
    txid = db.Column(db.String(255),default='',nullable=False)
    id_user = db.Column(db.Integer(), index=True)
    provider = db.Column(db.String(255),default='',nullable=False)
    address = db.Column(db.String(255),default='',nullable=False)
    transaction_type = db.Column(db.String(255),default='',nullable=False, index=True)
    currency = db.Column(db.String(255),default='',nullable=False, index=True)
    amount = db.Column(db.Numeric(14, 6), default=0)
    blockhash = db.Column(db.String(255),default='',nullable=False)
    blockindex = db.Column(db.String(255),default='',nullable=False)
    hex = db.Column(db.String(255),default='',nullable=False)
    blocktime = db.Column(db.String(255),default='',nullable=False)
    confirmations = db.Column(db.String(255),default='',nullable=False)
    timereceived = db.Column(db.String(255),default='',nullable=False)
    time = db.Column(db.String(255),default='',nullable=False)

    status = db.Column(db.Integer(),default=1,nullable=False)
    # 1 - da esegure
    # > 2 - errore
    # eseguito

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Transaction %r>' % (self.name)

class Volumes(db.Model):
    # internal fields
    id = db.Column(db.Integer(), primary_key=True)
    currency = db.Column(db.String(255),default='',nullable=False, index=True)
    volume = db.Column(db.Numeric(14, 6), default=0)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Transaction %s %s>' % (self.currency, self.volume)


class UserWallet(db.Model):
    # internal fields
    id = db.Column(db.Integer(), primary_key=True)
    id_user = db.Column(db.Integer(), index=True)
    currency = db.Column(db.String(255),default='',nullable=False)
    address = db.Column(db.String(255),default='',nullable=False)
    flag_used = db.Column(db.Integer(),default=0,nullable=False)

    # create and modifiy time
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())

    def __repr__(self):
        return '<Transaction %r>' % (self.name)
