from decimal import Decimal
import uuid
import datetime

from flask_user import login_required, current_user
from flask import render_template, session, request, redirect, url_for, flash
import pytz

from ibwt.app_and_db import app, db_adapter, socketio
from ibwt.orders.forms import BuyForm, SellForm
from ibwt.users.models import User
from ibwt.orders.models import Buy, Sell, TradeData, Transaction
from ibwt.startup import currencies_settings
from ibwt.chat.models import Message



@app.route('/buy', methods=['POST',])
@login_required
def buy_order():
    currency = session['currencies'][0]
    currency2 = session['currencies'][1]
    if not check_currencies(currency, currency2):
        del session['currencies']
        flash('Currency combination invalid', 'error')
        return redirect(url_for('home_page'))

    buy_form = BuyForm(request.form)
    buy_form.currency=currency
    buy_form.currency2=currency2
    buy_form.fee=currencies_settings.FEE_PER_CURRENCIES[currency]

    fee_percentage = currencies_settings.FEE_PER_CURRENCIES[currency]

    sell_form = SellForm()
    sell_form.currency=currency
    sell_form.currency2=currency2
    sell_form.fee=fee_percentage

    if request.method == 'POST' and buy_form.validate():
        cost = Decimal(buy_form.amount.data) * Decimal(buy_form.price_per_unit.data)
        user_amount = getattr(current_user,currency2)
        if cost >= user_amount:
            flash('You don\'t have enough funds. Please recharge', 'error')
        else:
            # calculate
            amount = Decimal(buy_form.amount.data)
            fee_percentage = Decimal(fee_percentage)
            price_per_unit = Decimal(buy_form.price_per_unit.data)

            fee = (fee_percentage / Decimal('100')) * amount
            total_order = amount * price_per_unit
            total_order_no_fee = total_order - fee

            oid = uuid.uuid4().hex

            ins_ts = datetime.datetime.utcnow()
            ins_ts = pytz.utc.localize(ins_ts)

            amount_clean = amount - fee
            db_adapter.add_object(Buy,
                                      uuid = oid,
                                      uid=current_user.id,
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
            user_update_fund = db_adapter.find_first_object(User,id=current_user.id)
            new_amount = user_amount - cost
            db_adapter.update_object(user_update_fund,
                                      **{currency2: new_amount})
            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                            uuid=tid,
                                              amount=amount,
                                              currency=currency2,
                                              id_user=current_user.id,
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


            db_adapter.commit()
            flash('Order set successfully', 'success')

            # send broadcast to connected user
            data_emit = {'uuid': oid}
            emit_order('newborder', data_emit)

        return redirect(url_for('home_page'))

    return render_template('pages/home_page.html',
                           currency=currency,
                           currency2=currency2,
                           buy_form=buy_form,
                           sell_form=sell_form)

@app.route('/sell', methods=['POST',])
@login_required
def sell_order():
    currency = session['currencies'][0]
    currency2 = session['currencies'][1]

    if not check_currencies(currency, currency2):
        del session['currencies']
        flash('Currency combination invalid', 'error')
        return redirect(url_for('home_page'))

    buy_form = BuyForm()
    buy_form.currency=currency
    buy_form.currency2=currency2
    buy_form.fee=currencies_settings.FEE_PER_CURRENCIES[currency]

    fee_percentage = currencies_settings.FEE_PER_CURRENCIES[currency]

    sell_form = SellForm(request.form)
    sell_form.currency=currency
    sell_form.currency2=currency2
    sell_form.fee=currencies_settings.FEE_PER_CURRENCIES[currency]

    if request.method == 'POST' and sell_form.validate():
        amount = Decimal(sell_form.amount.data)
        cost = Decimal(sell_form.amount.data) * Decimal(sell_form.price_per_unit.data)
        user_amount = getattr(current_user,currency)
        if amount >= user_amount:
            flash('You don\'t have enough funds. Please recharge', 'error')
        else:
            # calculate
            fee_percentage = Decimal(fee_percentage)
            price_per_unit = Decimal(sell_form.price_per_unit.data)

            fee = (fee_percentage / Decimal('100')) * amount
            total_order = amount * price_per_unit
            total_order_no_fee = total_order - fee

            ins_ts = datetime.datetime.utcnow()
            ins_ts = pytz.utc.localize(ins_ts)

            oid = uuid.uuid4().hex
            amount_clean = amount - fee
            db_adapter.add_object(Sell,
                                      uuid = oid,
                                      uid=current_user.id,
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
            user_update_fund = db_adapter.find_first_object(User,id=current_user.id)
            new_amount = user_amount - amount
            db_adapter.update_object(user_update_fund,
                                      **{currency: new_amount})

            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                            uuid=tid,
                                              amount=amount,
                                              currency=currency,
                                              id_user=current_user.id,
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

            db_adapter.commit()
            flash('Order set successfully', 'success')

            # send broadcast to connected user
            data_emit = {'uuid': oid}
            emit_order('newsorder', data_emit)


        return redirect(url_for('home_page'))

    return render_template('pages/home_page.html',
                           currency=currency,
                           currency2=currency2,
                           buy_form=buy_form,
                           sell_form=sell_form)


@app.route('/cancel/<type_order>/<id>')
@login_required
def cancel_order(id, type_order):
    order = None
    if type_order == 'buy':
        order = db_adapter.find_first_object(Buy,
                                             uuid=id)
    elif type_order == 'sell':
        order = db_adapter.find_first_object(Sell,
                                             uuid=id)
    else:
        flash('order type %s unrecognized' % type, 'error')
        return redirect(url_for('user_orders_page'))

    if not order:
        flash('order already deleted or closed', 'error' )
        return redirect(url_for('user_orders_page'))

    if order.flag_completed == 1:
        flash('order closed', 'error' )
        return redirect(url_for('user_orders_page'))

    user = db_adapter.find_first_object(User, id=current_user.id)
    currency = order.currency
    currency2 = order.currency2
    # BUY
    if type_order == 'buy':
        # check if order amout is 0
        # payback to user all amount + fee
        currency_update = currency2
        if order.amount == order.amount_start:
            order_amount = order.total_order
            fee_applied = order.initial_fee
            new_amount = getattr(current_user,currency_update) + order_amount

            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                              uuid=tid,
                                              amount=order_amount,
                                              currency=currency_update,
                                              id_user=current_user.id,
                                              provider='ibwt',
                                              status=0,
                                              transaction_type='accredit')

            db_adapter.delete_object(order)
            db_adapter.update_object(user,**({currency_update: new_amount}))
            db_adapter.commit()

            flash('Order closed. Your account has been refunded with %s %s' % (order_amount, currency_update), 'success' )
        else:
            order_amount = order.amount
            actual_fee = order.fee
            initial_amount = order.amount_start_no_fee
            amount_to_add = initial_amount - (order_amount + actual_fee)
            new_amount = getattr(current_user,currency_update) + amount_to_add

             # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                            uuid=tid,
                                              amount=amount_to_add,
                                              currency=currency_update,
                                              id_user=current_user.id,
                                              provider='ibwt',
                                              status=0,
                                              transaction_type='accredit')


            db_adapter.delete_object(order)
            db_adapter.update_object(user,**({currency_update: new_amount}))
            db_adapter.commit()

            flash('Order closed. Your account has been refunded with %s %s' % (amount_to_add, currency_update), 'success' )
        return redirect(url_for('user_orders_page'))

     # SELL
    elif type_order == 'sell':
        # check if order amout is 0
        # payback to user all amount + fee
        currency_update = currency
        if order.amount == order.amount_start:
            currency_update = currency
            order_amount = order.amount
            fee_applied = order.initial_fee
            amount_to_add = order_amount + fee_applied
            new_amount = getattr(current_user,currency_update) + amount_to_add

            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                              uuid=tid,
                                              amount=amount_to_add,
                                              currency=currency_update,
                                              id_user=current_user.id,
                                              provider='ibwt',
                                              status=0,
                                              transaction_type='accredit')

            db_adapter.delete_object(order)
            db_adapter.update_object(user,**({currency_update: new_amount}))
            db_adapter.commit()
            flash('Order closed. Your account has been refunded with %s %s' % (amount_to_add, currency_update), 'success' )
        else:
            order_amount = order.amount
            actual_fee = order.fee
            initial_amount = order.amount_start_no_fee
            amount_to_add = initial_amount - (order_amount + actual_fee)
            new_amount = getattr(current_user,currency_update) + amount_to_add

            # write it in history transaction
            tid = uuid.uuid4().hex
            db_adapter.add_object(Transaction,
                                              uuid=tid,
                                              amount=amount_to_add,
                                              currency=currency_update,
                                              id_user=current_user.id,
                                              provider='ibwt',
                                              status=0,
                                              transaction_type='accredit')

            db_adapter.delete_object(order)
            db_adapter.update_object(user,**({currency_update: new_amount}))
            db_adapter.commit()
            flash('Order closed. Your account has been refunded with %s %s' % (amount_to_add, currency_update), 'success' )
        return redirect(url_for('user_orders_page'))

    flash('Cancel error please. Try again.', 'error')
    return redirect(url_for('user_orders_page'))


def emit_order(type, data):
    json_resp = {}
    json_resp['uuid'] = data['uuid']
    #socketio.emit(type, json_resp, namespace='/orders')



def check_currencies(currency, currency2):
    if currency not in app.config['IBWT_CURRENCIES'] or \
        currency2 not in app.config['IBWT_CURRENCIES'] or\
            (currency, currency2) not in app.config['EXCHANGABLE_CURRENCIES']:
        return False
    return True
