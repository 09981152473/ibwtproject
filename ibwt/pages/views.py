from decimal import Decimal
import decimal

from flask import render_template, session, g, request, url_for, jsonify
from flask_user import login_required, roles_required, current_user
import flask_sijax
from sqlalchemy.sql import func
from flask_debugtoolbar_lineprofilerpanel.profile import line_profile
import pytz

from ibwt.orders.forms import BuyForm, SellForm
from ibwt.startup import currencies_settings
from ibwt.app_and_db import app
from ibwt.app_and_db import format_locale_number, format_datetime
from ibwt.orders.models import Buy, Sell, BuyHistory, SellHistory, TradeData, Volumes, Transaction
from ibwt.users.models import UserDepositWithdrawal
from ibwt.chat.models import Message

# The Home page is accessible to anyone
@app.route('/')
@line_profile
def home_page():
    if not 'currencies' in session:
        session['currencies'] = app.config['DEFAULT_EXCHANGABLE_CURRENCIES']
    currency = session['currencies'][0]
    currency2 = session['currencies'][1]

    buy_form = BuyForm(request.form)
    buy_form.currency=currency
    buy_form.currency2=currency2
    buy_form.fee=currencies_settings.FEE_PER_CURRENCIES[currency]


    sell_form = SellForm(request.form)
    sell_form.currency=currency
    sell_form.currency2=currency2
    sell_form.fee=currencies_settings.FEE_PER_CURRENCIES[currency]

    return render_template('pages/home_page.html',
                           currency=currency,
                           currency2=currency2,
                           buy_form=buy_form,
                           sell_form=sell_form)

# The Member page is accessible to authenticated users (users that have logged in)
@app.route('/member')
@login_required             # Limits access to authenticated users
def member_page():
    return render_template('pages/member_page.html')

# The Admin page is accessible to users with the 'admin' role
@app.route('/admin')
@roles_required('admin')    # Limits access to users with the 'admin' role
def admin_page():
    return render_template('pages/admin_page.html')

@app.route('/chart.json', methods=['POST', 'GET'])
@line_profile
def json_chart():
    if not 'currencies' in session:
        session['currencies'] = app.config['DEFAULT_EXCHANGABLE_CURRENCIES']
    currency = session['currencies'][0]
    currency2 = session['currencies'][1]
    local_tz = pytz.timezone(g.timezone)

    d_years = {}
    d_months = {}
    d_days = {}
    d_hours = {}
    d_minutes = {}
    sell_orders = Sell.query.filter_by(currency=currency,currency2=currency2)
    buy_orders = Buy.query.filter_by(currency=currency,currency2=currency2)

    for sell_order in sell_orders:

        list_keys = []
        list_keys.append((sell_order.created_date.strftime('%Y-%m-%d 00:00:00'), d_days))
        list_keys.append((sell_order.created_date.strftime('%Y-%m-%d %H:00:00'), d_hours))
        list_keys.append((sell_order.created_date.strftime('%Y-%m-%d %H:%M:00'), d_minutes))

        for (key, dictionary) in list_keys:
            if key not in dictionary:
                dictionary[key] = {}
                dictionary[key]['datetime'] = pytz.utc.localize(datetime.datetime(sell_order.created_date.year,
                                                                                  sell_order.created_date.month,
                                                                                  sell_order.created_date.day,
                                                                                  sell_order.created_date.hour,
                                                                                  sell_order.created_date.minute))
                dictionary[key]['open'] = sell_order.price_per_unit
                dictionary[key]['close'] = sell_order.price_per_unit
                dictionary[key]['high'] = sell_order.price_per_unit
                dictionary[key]['low'] = sell_order.price_per_unit
                dictionary[key]['open_ts'] = sell_order.created_date
                dictionary[key]['end_ts'] = sell_order.created_date
                dictionary[key]['volume'] = decimal.Decimal('0')

            if sell_order.created_date < dictionary[key]['open_ts']:
                dictionary[key]['open'] = sell_order.price_per_unit
                dictionary[key]['open_ts'] = sell_order.created_date

            if sell_order.created_date > dictionary[key]['end_ts']:
                dictionary[key]['close'] = sell_order.price_per_unit
                dictionary[key]['end_ts'] = sell_order.created_date

            if sell_order.price_per_unit > dictionary[key]['high']:
                dictionary[key]['high'] = sell_order.price_per_unit

            if sell_order.price_per_unit < dictionary[key]['low']:
                dictionary[key]['low'] = sell_order.price_per_unit

            dictionary[key]['volume'] += sell_order.amount_start

    for buy_order in buy_orders:

        list_keys = []
        list_keys.append((buy_order.created_date.strftime('%Y-%m-%d'), d_days))
        list_keys.append((buy_order.created_date.strftime('%Y-%m-%d %H'), d_hours))
        list_keys.append((buy_order.created_date.strftime('%Y-%m-%d %H:%M'), d_minutes))
        list_keys.append((buy_order.created_date.strftime('%Y-%m-%d %H:%M:%s'), d_minutes))

        for (key, dictionary) in list_keys:
            if key not in dictionary:
                dictionary[key] = {}
                dictionary[key]['datetime'] =  pytz.utc.localize(datetime.datetime(buy_order.created_date.year,
                                                                                   buy_order.created_date.month,
                                                                                   buy_order.created_date.day,
                                                                                   buy_order.created_date.hour,
                                                                                   buy_order.created_date.minute))
                dictionary[key]['open'] = buy_order.price_per_unit
                dictionary[key]['close'] = buy_order.price_per_unit
                dictionary[key]['high'] = buy_order.price_per_unit
                dictionary[key]['low'] = buy_order.price_per_unit
                dictionary[key]['open_ts'] = buy_order.created_date
                dictionary[key]['end_ts'] = buy_order.created_date
                dictionary[key]['volume'] = decimal.Decimal('0')

            if buy_order.created_date < dictionary[key]['open_ts']:
                dictionary[key]['open'] = buy_order.price_per_unit
                dictionary[key]['open_ts'] = buy_order.created_date

            if buy_order.created_date > dictionary[key]['end_ts']:
                dictionary[key]['close'] = buy_order.price_per_unit
                dictionary[key]['end_ts'] = buy_order.created_date

            if buy_order.price_per_unit > dictionary[key]['high']:
                dictionary[key]['high'] = buy_order.price_per_unit

            if buy_order.price_per_unit < dictionary[key]['low']:
                dictionary[key]['low'] = buy_order.price_per_unit

            dictionary[key]['volume'] += buy_order.amount_start

    out = []
    for minutes in d_minutes:

        app.logger.debug(d_minutes[minutes]['datetime'])
        local_dt = d_minutes[minutes]['datetime'].astimezone(local_tz)
        local_user_date_time = local_tz.normalize(local_dt)
        local_user_date_time_str = format_datetime(local_user_date_time, 'yyyy/MM/dd H:mm:SS')
        final_datetime = datetime.datetime.strptime(local_user_date_time_str, "%Y/%m/%d %H:%M:%S")

        out.append([int(unix_time_millis(final_datetime)),
                    d_minutes[minutes]['open'],
                    d_minutes[minutes]['high'],
                    d_minutes[minutes]['low'],
                    d_minutes[minutes]['close'],
                    d_minutes[minutes]['volume'],
                    ])
    out.sort()

    return jsonify(result=out)

import datetime

def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return unix_time(dt) * 1000.0



# Functions registered with @flask_sijax.route can use Sijax
@flask_sijax.route(app, '/9c189051675bf047a965e835814')
def ajax():

    def calculate_total(obj_response, amount, price_per_unit, form_id):
        json_resp = {}
        if not 'currencies' in session:
            session['currencies'] = app.config['DEFAULT_EXCHANGABLE_CURRENCIES']
        currency = session['currencies'][0]
        currency2 = session['currencies'][1]
        fee = currencies_settings.FEE_PER_CURRENCIES[currency]

        total_order = (Decimal(amount) * Decimal(price_per_unit)) + Decimal(str(fee))
        total_order_formatted = format_locale_number(total_order)

        json_resp['fee']  = format_locale_number(fee)
        json_resp['total_order'] = total_order_formatted
        json_resp['form_id'] = form_id
        obj_response.call('render_fee_total', [json_resp,])

    def get_latest_buy_orders(obj_response):
        json_resp = {}
        user_orders = Buy.query.filter_by(currency=session['currencies'][0],
                                          currency2=session['currencies'][1]).order_by(Buy.created_date.desc()).limit(100)
        html = render_template('orders/latest_buy_orders.html',
                               user_orders=user_orders)
        json_resp['html'] = html
        obj_response.call('render_latest_buy_orders', [json_resp,])

    def get_latest_sell_orders(obj_response):
        json_resp = {}
        user_orders = Sell.query.filter_by(currency=session['currencies'][0],
                                           currency2=session['currencies'][1]).order_by(Sell.created_date.desc()).limit(100)
        html = render_template('orders/latest_sell_orders.html',
                               user_orders=user_orders)

        json_resp['html'] = html
        obj_response.call('render_latest_sell_orders', [json_resp,])

    def get_grouped_sell_orders(obj_response):
        json_resp = {}
        user_orders = Sell.query.with_entities(func.sum(Sell.amount).label('amount'),
                                               Sell.price_per_unit,
                                               Sell.currency,
                                               Sell.currency2,
                                               func.sum(Sell.total_order).label('total_order'),
                                               ) \
            .filter_by(currency=session['currencies'][0],
                       currency2=session['currencies'][1]) \
            .group_by(Sell.price_per_unit) \
            .order_by(Sell.created_date.desc()) \
            .limit(100)
        html = render_template('orders/grouped_sell_orders.html',
                               user_orders=user_orders)
        json_resp['html'] = html
        obj_response.call('render_grouped_sell_orders', [json_resp,])

    def get_grouped_buy_orders(obj_response):
        json_resp = {}
        user_orders = Buy.query.with_entities(func.sum(Buy.amount).label('amount'),
                                              Buy.price_per_unit,
                                              Buy.currency,
                                              Buy.currency2,
                                              func.sum(Buy.total_order).label('total_order'),
                                              ) \
            .filter_by(currency=session['currencies'][0],
                       currency2=session['currencies'][1]) \
            .group_by(Buy.price_per_unit) \
            .order_by(Buy.created_date.desc()) \
            .limit(100)
        html = render_template('orders/grouped_buy_orders.html',
                               user_orders=user_orders)

        json_resp['html'] = html
        obj_response.call('render_grouped_buy_orders', [json_resp,])

    def get_buy_order_by_uuid(obj_response, data):
        json_resp = {}
        buy_order = Buy.query.filter_by(uuid=data['uuid']).first()
        json_resp['html'] = render_template('orders/latest_buy_orders_row.html',order = buy_order)
        obj_response.call('render_buy_order_row', [json_resp,])

    def get_sell_order_by_uuid(obj_response, data):
        json_resp = {}
        sell_order = Sell.query.filter_by(uuid=data['uuid']).first()
        json_resp['html'] = render_template('orders/latest_sell_orders_row.html',order = sell_order)
        obj_response.call('render_sell_order_row', [json_resp,])

    def get_trade_data(obj_response):
        json_resp = {}
        json_resp['max_sell_price'] = 0
        json_resp['min_buy_price'] = 0
        json_resp['currency_volume'] = 0
        json_resp['currency2_volume'] = 0
        json_resp['total_orders'] = 0
        json_resp['total_buy_orders'] = 0
        json_resp['total_sell_orders'] = 0

        json_resp['max_sell_price_raw'] = 0
        json_resp['min_buy_price_raw'] = 0
        if not 'currencies' in session:
            session['currencies'] = app.config['DEFAULT_EXCHANGABLE_CURRENCIES']
        currency = session['currencies'][0]
        currency2 = session['currencies'][1]

        trade_data = TradeData.query.filter_by(currency=currency,
                                               currency2=currency2).first()
        currency_volume = Volumes.query.filter_by(currency=currency).first()
        currency2_volume = Volumes.query.filter_by(currency=currency2).first()

        if trade_data:
            json_resp['max_sell_price'] = format_locale_number(trade_data.max_sell_price)
            json_resp['min_buy_price'] = format_locale_number(trade_data.min_buy_price)
            json_resp['max_sell_price_raw'] = trade_data.max_sell_price
            json_resp['min_buy_price_raw'] = trade_data.min_buy_price

        if currency_volume:
            json_resp['currency_volume'] = format_locale_number(currency_volume.volume)

        if currency2_volume:
            json_resp['currency2_volume'] = format_locale_number(currency2_volume.volume)

        obj_response.call('render_trade_data', [json_resp,])

    def get_messages_chat(obj_response):
        json_resp = {}
        messages = Message.objects.filter(locale=g.locale).order_by('-at')[:50]
        json_resp['html'] = render_template('base_templates/base_chat.html',
                                            messages=messages)

        obj_response.call('render_chat_messages', [json_resp,])


    def get_user_open_sell_orders(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        user_orders = []

        sell_open_orders = Sell.query.filter_by(uid=current_user.id,
                                                flag_completed=2).order_by(Sell.last_updated.desc())

        json_resp['html'] = render_template('users/panels/sell_orders_open.html',
                                            sell_open_orders=sell_open_orders,
        )

        obj_response.call('render_user_open_sell_orders', [json_resp,])

    def get_user_open_buy_orders(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        user_orders = []

        buy_open_orders = Buy.query.filter_by(uid=current_user.id,
                                                flag_completed=2).order_by(Buy.last_updated.desc())

        json_resp['html'] = render_template('users/panels/buy_orders_open.html',
                                            buy_open_orders=buy_open_orders,
        )

        obj_response.call('render_user_open_buy_orders', [json_resp,])


    def get_user_orders(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        user_orders = []
        user_orders.extend(BuyHistory.query.filter_by(
            uid=current_user.id,
            currency=g.currency,
            currency2=g.currency2))

        user_orders.extend(SellHistory.query.filter_by(
            uid=current_user.id,
            currency=g.currency,
            currency2=g.currency2))

        json_resp['html'] = render_template('users/user_orders_list.html',
                                            user_orders=user_orders)

        obj_response.call('render_user_orders', [json_resp,])

    def get_user_latest_transactions(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        user_orders = []
        accredits = Transaction.query.filter_by(id_user=current_user.id,
                                                transaction_type='accredit'
                                                  ).order_by(Transaction.created_date.desc()).limit(10)

        charges = Transaction.query.filter_by(id_user=current_user.id,
                                                transaction_type='charge'
                                                  ).order_by(Transaction.created_date.desc()).limit(10)



        json_resp['html'] = render_template('users/panels/latest_transactions.html',
                                            accredits=accredits,
                                            charges=charges)

        obj_response.call('render_user_latest_transactions', [json_resp,])

    def get_user_transactions(obj_response, currency, transaction_type):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        transactions = []
        if transaction_type:
            if currency:
                transactions.extend(Transaction.query.filter_by(id_user=current_user.id,
                                                transaction_type=transaction_type,
                                                currency=currency
                                                  ).order_by(Transaction.created_date.desc())
                )
            else:
                transactions.extend(Transaction.query.filter_by(id_user=current_user.id,
                                                transaction_type=transaction_type,
                                                  ).order_by(Transaction.created_date.desc())
                )
        else:
            if currency:
                transactions.extend(Transaction.query.filter_by(id_user=current_user.id,
                                                currency=currency
                                                  ).order_by(Transaction.created_date.desc())
                )
            else:
                transactions.extend(Transaction.query.filter_by(id_user=current_user.id,
                                                  ).order_by(Transaction.created_date.desc())
                )

        transactions.sort(key=lambda x: x.created_date, reverse=True)


        json_resp['html'] = render_template('users/user_transactions_list.html',
                                            transactions=transactions)

        obj_response.call('render_user_transactions', [json_resp,])

    def get_user_deposits_withdrawals(obj_response, currency, transaction_type):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        transactions = []
        if transaction_type:
            if currency:
                transactions.extend(UserDepositWithdrawal.query.filter_by(id_user=current_user.id,
                                                transaction_type=transaction_type,
                                                currency=currency
                                                  ).order_by(UserDepositWithdrawal.created_date.desc())
                )
            else:
                transactions.extend(UserDepositWithdrawal.query.filter_by(id_user=current_user.id,
                                                transaction_type=transaction_type,
                                                  ).order_by(UserDepositWithdrawal.created_date.desc())
                )
        else:
            if currency:
                transactions.extend(UserDepositWithdrawal.query.filter_by(id_user=current_user.id,
                                                currency=currency
                                                  ).order_by(UserDepositWithdrawal.created_date.desc())
                )
            else:
                transactions.extend(UserDepositWithdrawal.query.filter_by(id_user=current_user.id,
                                                  ).order_by(UserDepositWithdrawal.created_date.desc())
                )

        transactions.sort(key=lambda x: x.created_date, reverse=True)


        json_resp['html'] = render_template('users/user_deposits_withdrawals_list.html',
                                            transactions=transactions)

        obj_response.call('render_user_transactions', [json_resp,])


    def get_user_total_orders(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        user_orders = []

        json_resp['total_buy_orders'] = Buy.query.filter_by(uid=current_user.id).count()
        json_resp['total_sell_orders'] = Sell.query.filter_by(uid=current_user.id).count()

        json_resp['total_history_buy_order'] = BuyHistory.query.filter_by(uid=current_user.id).count()
        json_resp['total_history_sell_order'] = SellHistory.query.filter_by(uid=current_user.id).count()

        json_resp['total_orders'] = json_resp['total_buy_orders'] + json_resp['total_sell_orders'] +\
                                     json_resp['total_history_buy_order'] + json_resp['total_history_sell_order']
        json_resp['total_open_orders'] = json_resp['total_buy_orders'] + json_resp['total_sell_orders']
        json_resp['total_closed_orders'] = json_resp['total_history_buy_order'] + json_resp['total_history_sell_order']

        for k in json_resp:
            json_resp[k] = format_locale_number(json_resp[k])

        obj_response.call('render_user_total_orders', [json_resp,])


    def get_user_latest_closed_orders(obj_response):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        json_resp['html'] = ''

        closed_orders = []
        closed_orders.extend(BuyHistory.query.filter_by(uid=current_user.id))
        closed_orders.extend(SellHistory.query.filter_by(uid=current_user.id))
        closed_orders.sort(key=lambda x: x.last_updated, reverse=True)

        json_resp['html'] = render_template('users/panels/latest_closed_orders.html',
                                            closed_orders=closed_orders)


        obj_response.call('render_user_latest_closed_orders', [json_resp,])



    def get_user_open_orders(obj_response, currency, currency2, order_type):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        json_resp['html'] = ''

        open_orders = []
        if not currency or not currency2:
            if order_type not in ('buy', 'sell'):
                open_orders.extend(Buy.query.filter_by(uid=current_user.id))
                open_orders.extend(Sell.query.filter_by(uid=current_user.id))
            else:
                if order_type == 'buy':
                    open_orders.extend(Buy.query.filter_by(uid=current_user.id))
                else:
                    open_orders.extend(Sell.query.filter_by(uid=current_user.id))
        else:
            if order_type not in ('buy', 'sell'):
                open_orders.extend(Buy.query.filter_by(uid=current_user.id,
                                                       currency=currency,
                                                       currency2=currency2))
                open_orders.extend(Sell.query.filter_by(uid=current_user.id,
                                                       currency=currency,
                                                       currency2=currency2))
            else:
                if order_type == 'buy':
                    open_orders.extend(Buy.query.filter_by(uid=current_user.id,
                                                           currency=currency,
                                                           currency2=currency2))
                else:
                    open_orders.extend(Sell.query.filter_by(uid=current_user.id,
                                                           currency=currency,
                                                           currency2=currency2))

        open_orders.sort(key=lambda x: x.last_updated, reverse=True)

        json_resp['html'] = render_template('users/user_orders_list.html',
                                            open_orders=open_orders)


        obj_response.call('render_user_open_orders', [json_resp,])


    def get_user_closed_orders(obj_response, currency, currency2, order_type):
        if not current_user.is_authenticated():
            obj_response.redirect(url_for('home_page'))

        json_resp = {}
        json_resp['html'] = ''

        open_orders = []
        if not currency or not currency2:
            if order_type not in ('buy', 'sell'):
                open_orders.extend(BuyHistory.query.filter_by(uid=current_user.id))
                open_orders.extend(SellHistory.query.filter_by(uid=current_user.id))
            else:
                if order_type == 'buy':
                    open_orders.extend(BuyHistory.query.filter_by(uid=current_user.id))
                else:
                    open_orders.extend(SellHistory.query.filter_by(uid=current_user.id))
        else:
            if order_type not in ('buy', 'sell'):
                open_orders.extend(BuyHistory.query.filter_by(uid=current_user.id,
                                                       currency=currency,
                                                       currency2=currency2))
                open_orders.extend(SellHistory.query.filter_by(uid=current_user.id,
                                                       currency=currency,
                                                       currency2=currency2))
            else:
                if order_type == 'buy':
                    open_orders.extend(BuyHistory.query.filter_by(uid=current_user.id,
                                                           currency=currency,
                                                           currency2=currency2))
                else:
                    open_orders.extend(SellHistory.query.filter_by(uid=current_user.id,
                                                           currency=currency,
                                                           currency2=currency2))

        open_orders.sort(key=lambda x: x.last_updated, reverse=True)

        json_resp['html'] = render_template('users/user_orders_closed_list.html',
                                            open_orders=open_orders)


        obj_response.call('render_user_open_orders', [json_resp,])


    if g.sijax.is_sijax_request:
        # Sijax request detected - let Sijax handle it
        g.sijax.register_callback('calculate_total', calculate_total)
        g.sijax.register_callback('get_latest_buy_orders', get_latest_buy_orders)
        g.sijax.register_callback('get_latest_sell_orders', get_latest_sell_orders)
        g.sijax.register_callback('get_grouped_sell_orders', get_grouped_sell_orders)
        g.sijax.register_callback('get_grouped_buy_orders', get_grouped_buy_orders)
        g.sijax.register_callback('get_buy_order_by_uuid', get_buy_order_by_uuid)
        g.sijax.register_callback('get_sell_order_by_uuid', get_sell_order_by_uuid)
        g.sijax.register_callback('get_trade_data', get_trade_data)
        g.sijax.register_callback('get_messages_chat', get_messages_chat)

        # user ajax
        g.sijax.register_callback('get_user_open_sell_orders', get_user_open_sell_orders)
        g.sijax.register_callback('get_user_open_buy_orders', get_user_open_buy_orders)
        g.sijax.register_callback('get_user_latest_transactions', get_user_latest_transactions)
        g.sijax.register_callback('get_user_total_orders', get_user_total_orders)
        g.sijax.register_callback('get_user_latest_closed_orders', get_user_latest_closed_orders)
        g.sijax.register_callback('get_user_open_orders', get_user_open_orders)
        g.sijax.register_callback('get_user_closed_orders', get_user_closed_orders)
        g.sijax.register_callback('get_user_transactions', get_user_transactions)
        g.sijax.register_callback('get_user_deposits_withdrawals', get_user_deposits_withdrawals)

        return g.sijax.process_request()


    # Regular (non-Sijax request) - render the page template
    return 'Not Authorized'