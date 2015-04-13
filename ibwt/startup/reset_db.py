from __future__ import print_function
import datetime
import random, decimal
import core

from ibwt.app_and_db import app, db, db_adapter
from ibwt.startup.init_app import init_app
from ibwt.users.models import User, UserAuth, Role
from ibwt.orders.models import Buy, BuyHistory, SellBuy, Sell, SellHistory, TradeData, Transaction, UserWallet, Volumes
from random import randrange, uniform, choice
from ibwt.startup import currencies_settings
from decimal import Decimal
import uuid, pytz

from ibwt.startup.currencies_settings import SITE_CURRENCIES, EXCHANGABLE_CURRENCIES

def reset_db(app, db):
    """
    Delete all tables; Create all tables; Populate roles and users.
    """

    # Drop all tables
    print('Dropping all tables')
    db.drop_all()

    # Create all tables
    print('Creating all tables')
    db.create_all()

    # Adding roles
    print('Adding roles')
    admin_role = Role(name='admin')
    db.session.add(admin_role)

    # Add users
    print('Adding users')
    list_users = []

    user = add_user(app, db, 'admin', 'Admin', 'User', 'admin@example.com', 'Password1')

    for currency in SITE_CURRENCIES:
        volume = Volumes(currency=currency, volume=0)
        db.session.add(volume)

        setattr(user, currency, decimal.Decimal(str(uniform(9000, 9999))))
    user.roles.append(admin_role)
    db.session.commit()

    print ('Adding random orders')
    users = db_adapter.find_all_objects(User)
    for u in users:
        list_users.append(u)

    for currency, currency2 in EXCHANGABLE_CURRENCIES:
        for i in range(1,100):
            user_pass = random.choice(list_users)
            order_type = random.choice(['buy', 'sell'])
            amount = uniform(1, 100)
            price_per_unit = uniform(0.0001, 10)
            add_order(app, db, user_pass, order_type, currency, currency2, amount, price_per_unit, db_adapter)
    db_adapter.commit()

    print ('Orders added')
    print ('Fullfil batch starting')
    core.main()
    print ('Fullfil batch ended')


def add_user(app, db, username, first_name, last_name, email, password):
    """
    Create UserAuth and User records.
    """
    user_auth = UserAuth(username=username, password=app.user_manager.hash_password(password))
    user = User(
        active=True,
        first_name=first_name,
        last_name=last_name,
        email=email,
        confirmed_at=datetime.datetime.now(),
        user_auth=user_auth
    )
    db.session.add(user_auth)
    db.session.add(user)
    return user


def add_order(app, db, user, order_type, currency, currency2, amount, price_per_unit, db_adapter):

    fee_percentage = currencies_settings.FEE_PER_CURRENCIES[currency]
    user_amount = getattr(user,currency)
    from datetime import datetime
    import random
    local_tz = pytz.timezone('Europe/Rome')
    year = random.choice([2013, 2014,2015])
    month = random.choice(range(1, 12))
    day = random.choice(range(1, 29))
    if year == 2015:
        month = random.choice(range(1, 4))
        day = random.choice(range(1, 5))

    hour = random.choice(range(8, 21))
    minute = random.choice(range(5, 20))
    second = random.choice(range(1, 60))
    ins_ts = local_tz.localize(datetime(year, month, day, hour, minute, second))
    ins_ts = ins_ts.replace(tzinfo=local_tz)


    if order_type == 'buy':
        cost = Decimal(amount) * Decimal(price_per_unit)
        if cost >= user_amount:
            return
        else:
            amount = Decimal(amount)
            fee_percentage = Decimal(fee_percentage)
            price_per_unit = Decimal(price_per_unit)

            fee = (fee_percentage / Decimal('100')) * amount
            total_order = amount * price_per_unit
            total_order_no_fee = total_order - fee

            oid = uuid.uuid4().hex


            amount_clean = amount - fee
            db_adapter.add_object(Buy,
                                      uuid = oid,
                                      uid=user.id,
                                      currency=currency,
                                      currency2=currency2,
                                      amount_start_no_fee=amount,
                                      amount_start=amount_clean,
                                      amount=amount_clean,
                                      diff=0,
                                      initial_fee=fee,
                                      fee=fee,
                                      fee_percentage=fee_percentage,
                                      price_per_unit=price_per_unit,
                                      total_order=total_order,
                                      total_order_no_fee=total_order_no_fee,
                                      flag_completed=0,
                                      created_date=ins_ts
                                      )
            user_update_fund = db_adapter.find_first_object(User,id=user.id)
            new_amount = user_amount - cost
            db_adapter.update_object(user_update_fund,
                                      **{currency2: new_amount})
            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                  uuid=tid,
                                              amount=amount,
                                              currency=currency2,
                                              id_user=user.id,
                                              provider='ibwt',
                                                status=0,
                                              transaction_type='charge')

            # write it in tradeData
            trade_data = db_adapter.find_first_object(TradeData,currency=currency, currency2=currency2)
            if not trade_data:
                db_adapter.add_object(TradeData,
                                                  currency=currency,
                                                  currency2=currency2,
                                                  max_sell_price=0,
                                                  min_buy_price=price_per_unit)

            else:
                if price_per_unit < trade_data.min_buy_price:
                    db_adapter.update_object(trade_data,
                                                      min_buy_price=price_per_unit)

    elif order_type == 'sell':
        amount = Decimal(amount)
        cost = Decimal(amount) * Decimal(price_per_unit)
        user_amount = getattr(user,currency)
        if cost >= user_amount:
            return
        else:
            # calculate
            fee_percentage = Decimal(fee_percentage)
            price_per_unit = Decimal(price_per_unit)

            fee = (fee_percentage / Decimal('100')) * amount
            total_order = amount * price_per_unit
            total_order_no_fee = total_order - fee


            oid = uuid.uuid4().hex
            amount_clean = amount - fee
            db_adapter.add_object(Sell,
                                      uuid = oid,
                                      uid=user.id,
                                      currency=currency,
                                      currency2=currency2,
                                      amount_start_no_fee=amount,
                                      amount_start=amount_clean,
                                      amount=amount_clean,
                                      initial_fee=fee,
                                      fee=fee,
                                      fee_percentage=fee_percentage,
                                      price_per_unit=price_per_unit,
                                      total_order=total_order,
                                      total_order_no_fee=total_order_no_fee,
                                      flag_completed=0,
                                      created_date=ins_ts
                                      )
            user_update_fund = db_adapter.find_first_object(User,id=user.id)
            new_amount = user_amount - amount
            db_adapter.update_object(user_update_fund,
                                      **{currency: new_amount})

            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                              uuid=tid,
                                              amount=amount,
                                              currency=currency,
                                              id_user=user.id,
                                              provider='ibwt',
                                                status=0,
                                              transaction_type='charge')
            # write it in tradeData
            trade_data = db_adapter.find_first_object(TradeData,currency=currency, currency2=currency2)
            if not trade_data:
                db_adapter.add_object(TradeData,
                                                  currency=currency,
                                                  currency2=currency2,
                                                  max_sell_price=price_per_unit,
                                                  min_buy_price=0)

            else:
                if price_per_unit > trade_data.max_sell_price:
                    db_adapter.update_object(trade_data,
                                                      max_sell_price=price_per_unit)

# Initialize the ibwt and reset the database
if __name__ == "__main__":
    init_app(app, db)
    reset_db(app, db)
