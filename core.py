from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ibwt.users.models import User
from ibwt.orders.models import Transaction, Buy, Sell,\
    SellBuy, SellHistory,\
    BuyHistory, Volumes
from ibwt.startup.currencies_settings import EXCHANGABLE_CURRENCIES
import uuid
import config

# an Engine, which the Session will use for connection
# resources
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session

class Fullfilment():
    def __init__(self):
        self.c1 = ''
        self.c2 = ''
        self.cl = []

    def currency(self, value):
        self.c1 = value

    def currency2(self, value):
        self.c2 = value

    def execute(self):
        print 'Starting...'

        currency_loop = []
        if self.c1 and self.c2:
            currency_loop = ((self.c1, self.c2),)
        else:
            currency_loop = self.currencies_list()

        print 'Going to use -> %s ' %(repr(currency_loop))

        # for every pair of currency
        for c1, c2 in currency_loop:
            # get sell orders
            session = Session()
            session.no_autoflush
            print 'CURRENCIES: %s %s ' % (c1, c2)
            rows = session.query(Sell).filter(Sell.currency==c1,
                                              Sell.currency2==c2)
            rows = sorted(rows, key=lambda k: k.created_date, reverse=False)

            currency_volume = session.query(Volumes).filter_by(currency=c1).first()
            #currency2_volume = session.query(Volumes).filter_by(currency=c2).first()
            print 'curre: %s ' % repr(currency_volume )

            for sell_order in rows:
                sell_order.uid = str(sell_order.uid)
                print ''
                print 'COMPUTE sell order: %s | price: %s | amount: %s' % \
                 (sell_order.id, sell_order.price_per_unit, sell_order.amount)
                # for each sell order
                # get all orders with same
                # currency
                rowsB = session.query(Buy).filter(Buy.currency==c1,
                                                  Buy.currency2==c2,
                                                  Buy.uid.notin_(sell_order.uid))
                rowsB = sorted(rowsB, key=lambda k: k.created_date, reverse=False)
                print rowsB
                # for each buy order check if its has the price
                # equal or higer of this sell order

                # get user sell
                sell_user = session.query(User).filter_by(id=sell_order.uid).first()
                for buy_order in rowsB:
                    print ''
                    print buy_order
                    if buy_order.flag_completed == 1:
                        print 'salto'
                        continue

                    buy_user = session.query(User).filter_by(id=buy_order.uid).first()

                    if buy_order.price_per_unit >= sell_order.price_per_unit:

                        print 'COMPATIBLE buy order: %s | price: %s | amount: %s' \
                        % (buy_order.id, buy_order.price_per_unit, buy_order.amount)

                        if sell_order.amount > 0:

                            init_buy_amount = buy_order.amount
                            init_sell_amount = sell_order.amount

                            # if the amount of buy order is equal/lower of the sell
                            if buy_order.amount <= sell_order.amount:

                                #decrease sell order by the amount of the buy
                                sell_order.amount -= buy_order.amount


                                #set sell order completed if the amount is 0
                                if not sell_order.amount:
                                    sell_order.flag_completed = 1

                                # integrate the buy user fund amount
                                setattr(buy_user,
                                        c1,
                                        getattr(buy_user,c1) + buy_order.amount)

                                # write it in history transaction
                                trans_buy = Transaction()
                                trans_buy.uuid = uuid.uuid4().hex
                                trans_buy.amount = buy_order.amount
                                trans_buy.currency = c1
                                trans_buy.status = 0
                                trans_buy.id_user = buy_user.id
                                trans_buy.provider = 'ibwt'
                                trans_buy.transaction_type = 'accredit'
                                session.add(trans_buy)

                                # integrate the sell user fund amount
                                due_to_sell_user = buy_order.amount * sell_order.price_per_unit
                                setattr(sell_user,
                                        c2,
                                        getattr(sell_user,c2) + due_to_sell_user)

                                # write it in history transaction
                                trans_sell = Transaction()
                                trans_sell.uuid = uuid.uuid4().hex
                                trans_sell.amount = due_to_sell_user
                                trans_sell.status = 0
                                trans_sell.currency = c2
                                trans_sell.id_user = sell_user.id
                                trans_sell.provider = 'ibwt'
                                trans_sell.transaction_type = 'accredit'
                                session.add(trans_sell)

                                # increment volume of currency
                                currency_volume.volume += buy_order.amount

                                # decrease to 0 buy order because it covers all sell order
                                buy_order.amount = 0
                                buy_order.flag_completed = 1


                                # calculate difference
                                # of the sell price (if the buy price is higer, otherwise it will be 0)
                                # by doing  buying price * quantity buy - selling price * quantity buy
                                buy_order.diff = (buy_order.price_per_unit * init_buy_amount) -(sell_order.price_per_unit * init_buy_amount)

                                # set buy order as partially filled
                                # if needed
                                if buy_order.amount > 0:
                                    buy_order.flag_completed = 2

                                # set sell order as partially filled
                                # if needed
                                if sell_order.amount > 0:
                                    sell_order.flag_completed = 2

                                # save the association
                                ass_total_order = buy_order.price_per_unit * init_buy_amount
                                ass_total_order_sell = sell_order.price_per_unit * init_buy_amount

                                session.add(SellBuy(
                                        sid = sell_order.uuid,
                                        bid = buy_order.uuid,
                                        usid = sell_order.uid,
                                        ubid = buy_order.uid,
                                        currency = c1,
                                        currency2 = c2,
                                        amount_of_buy = init_buy_amount,
                                        price_per_unit = buy_order.price_per_unit,
                                        price_per_unit_sell = sell_order.price_per_unit,
                                        total_order = ass_total_order,
                                        total_order_sell = ass_total_order_sell,
                                        diff = ass_total_order - ass_total_order_sell
                                ))


                                # if order is completed insert it on
                                # sell_history
                                if buy_order.flag_completed == 1:
                                    buy_history = BuyHistory()
                                    buy_history.order_type = 'buy'
                                    buy_history.id = buy_order.id
                                    buy_history.uuid = buy_order.uuid
                                    buy_history.uid = buy_order.uid
                                    buy_history.currency = buy_order.currency
                                    buy_history.currency2 = buy_order.currency2
                                    buy_history.amount_start_no_fee = buy_order.amount_start_no_fee
                                    buy_history.amount_start = buy_order.amount_start_no_fee
                                    buy_history.initial_fee = buy_order.initial_fee
                                    buy_history.fee_percentage = buy_order.fee_percentage
                                    buy_history.price_per_unit = buy_order.price_per_unit
                                    buy_history.total_order = buy_order.total_order
                                    buy_history.total_order_no_fee = buy_order.total_order_no_fee

                                    if buy_order.diff > 0:
                                        # integrate the change to buy user fund amount
                                        setattr(buy_user,
                                                c2,
                                                getattr(buy_user,c2) + buy_order.diff)

                                        # write it in history transaction the charge
                                        trans_buy_user = Transaction()
                                        trans_buy_user.uuid = uuid.uuid4().hex
                                        trans_buy_user.amount = buy_order.diff
                                        trans_buy_user.status = 0
                                        trans_buy_user.currency = c2
                                        trans_buy_user.id_user = buy_user.id
                                        trans_buy_user.provider = 'ibwt'
                                        trans_buy_user.transaction_type = 'accredit'
                                        session.add(trans_buy_user)


                                    session.add(buy_history)
                                    session.delete(buy_order)
                                else:
                                    session.add(buy_order)


                                # if order is completed insert it on
                                # sell_history
                                if sell_order.flag_completed == 1:
                                    sell_history = SellHistory()
                                    sell_history.order_type = 'sell'
                                    sell_history.id = sell_order.id
                                    sell_history.uuid = sell_order.uuid
                                    sell_history.uid = sell_order.uid
                                    sell_history.currency = sell_order.currency
                                    sell_history.currency2 = sell_order.currency2
                                    sell_history.amount_start_no_fee = sell_order.amount_start_no_fee
                                    sell_history.amount_start = sell_order.amount_start_no_fee
                                    sell_history.initial_fee = sell_order.initial_fee
                                    sell_history.fee_percentage = sell_order.fee_percentage
                                    sell_history.price_per_unit = sell_order.price_per_unit
                                    sell_history.total_order = sell_order.total_order
                                    sell_history.total_order_no_fee = sell_order.total_order_no_fee

                                    session.add(sell_history)
                                    session.delete(sell_order)
                                else:
                                    session.add(sell_order)

                                session.add(currency_volume)
                                session.add(sell_user)
                                session.add(buy_user)
                                session.commit()

                            # if buy order amout exceed sell order amount
                            elif buy_order.amount > sell_order.amount:
                                #decrease buy order by the amount of the sell
                                buy_order.amount -=  sell_order.amount

                                # integrate the user buy amount by the differnce
                                setattr(buy_user,
                                        c1,
                                        getattr(buy_user,c1) + sell_order.amount)

                                # write it in history transaction
                                trans_buy = Transaction()
                                trans_buy.uuid = uuid.uuid4().hex
                                trans_buy.amount = sell_order.amount
                                trans_buy.status = 0
                                trans_buy.currency = c1
                                trans_buy.id_user = buy_user.id
                                trans_buy.provider = 'ibwt'
                                trans_buy.transaction_type = 'accredit'
                                session.add(trans_buy)


                                # integrate the sell user fund amount
                                due_to_sell_user = sell_order.amount * sell_order.price_per_unit
                                setattr(sell_user,
                                        c2,
                                        getattr(sell_user,c2) + due_to_sell_user)

                                # write it in history transaction
                                trans_sell = Transaction()
                                trans_sell.uuid = uuid.uuid4().hex
                                trans_sell.amount = due_to_sell_user
                                trans_sell.amount = due_to_sell_user
                                trans_sell.currency = c2
                                trans_sell.status = 0
                                trans_sell.id_user = sell_user.id
                                trans_sell.provider = 'ibwt'
                                trans_sell.transaction_type = 'accredit'
                                session.add(trans_sell)


                                # calculate difference
                                # of the sell price (if the buy price is higer, otherwise it will be 0)
                                # by doing  buying price * quantity buy - selling price * quantity buy
                                buy_order.diff = (buy_order.price_per_unit * init_sell_amount) - (sell_order.price_per_unit * init_sell_amount)

                                # set buy order as partially filled
                                # if needed
                                if buy_order.amount > 0:
                                    buy_order.flag_completed = 2

                                sell_order.amount = 0
                                sell_order.flag_completed = 1

                                # save the association
                                ass_total_order = buy_order.price_per_unit * init_buy_amount
                                ass_total_order_sell = sell_order.price_per_unit * init_buy_amount
                                session.add(SellBuy(
                                        sid = sell_order.uuid,
                                        bid = buy_order.uuid,
                                        usid = sell_order.uid,
                                        ubid = buy_order.uid,
                                        currency = c1,
                                        currency2 = c2,
                                        amount_of_buy = init_buy_amount,
                                        price_per_unit = buy_order.price_per_unit,
                                        price_per_unit_sell = sell_order.price_per_unit,
                                        total_order = ass_total_order,
                                        total_order_sell = ass_total_order_sell,
                                        diff = ass_total_order - ass_total_order_sell
                                ))

                                # increment volume of currency
                                currency_volume.volume += sell_order.amount


                                # if order is completed insert it on
                                # sell_history
                                if sell_order.flag_completed == 1:
                                    sell_history = SellHistory()
                                    sell_history.order_type = 'sell'
                                    sell_history.uuid = sell_order.uuid
                                    sell_history.id = sell_order.id
                                    sell_history.uid = sell_order.uid
                                    sell_history.currency = sell_order.currency
                                    sell_history.currency2 = sell_order.currency2
                                    sell_history.amount_start_no_fee = sell_order.amount_start_no_fee
                                    sell_history.amount_start = sell_order.amount_start_no_fee
                                    sell_history.initial_fee = sell_order.initial_fee
                                    sell_history.fee_percentage = sell_order.fee_percentage
                                    sell_history.price_per_unit = sell_order.price_per_unit
                                    sell_history.total_order = sell_order.total_order
                                    sell_history.total_order_no_fee = sell_order.total_order_no_fee

                                    session.add(sell_history)
                                    session.delete(sell_order)
                                else:
                                    session.add(sell_order)

                                session.add(currency_volume)
                                session.add(buy_user)
                                session.add(buy_order)
                                session.add(sell_user)
                                session.commit()
            session.close()
    def currencies_list(self):
        if not self.cl:
            tuples = EXCHANGABLE_CURRENCIES
            for row in tuples:
                self.cl.append((row[0].upper(),
                                row[1].upper()))

        return self.cl


def main():
    f = Fullfilment()
    f.execute()

if __name__ == '__main__':
    main()