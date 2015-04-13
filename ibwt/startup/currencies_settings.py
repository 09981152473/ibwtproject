# -*- coding: utf-8 -*-
CRYPTO_CURRENCIES = ('BTC','LTC','NVC','PPC','NMC','DRK','QRK','XPM')
#BANK_CURRENCIES = ('EUR', 'USD','CNY', 'RUR')
BANK_CURRENCIES = []

IBWT_CURRENCIES = CRYPTO_CURRENCIES


SITE_CURRENCIES = {'BTC':('B','BitCoin'),
                   'LTC':('L','LiteCoin'),
                   'NVC':('N','NovaCoin'),
                   'PPC':('P','PeerCoin'),
                   'NMC':('NM','NameCoin'),
                   'DRK':('D','DarkCoin'),
          #        'URO':('U',''),
#                  'BTCD':('BD',''),
                   'QRK':('Q','QuarkCoin'),
#                  'DOGE':('DG',''),
                    'XPM':('X','PrimeCoin')
                    }


EXCHANGABLE_CURRENCIES = (('BTC', 'LTC'),
                        ('BTC', 'NVC'),
                        ('BTC', 'PPC'),
                        ('BTC', 'NMC'),
                        ('BTC', 'DRK'),
                        ('BTC', 'QRK'),
                        ('BTC', 'XPM'),
                        ('LTC', 'BTC'),
                        ('LTC', 'NVC'),
                        ('LTC', 'PPC'),
                        ('LTC', 'NMC'),
                        ('LTC', 'DRK'),
                        ('LTC', 'QRK'),
                        ('LTC', 'XPM'),
                        ('NVC', 'BTC'),
                        ('NVC', 'LTC'),
                        ('NVC', 'PPC'),
                        ('NVC', 'NMC'),
                        ('NVC', 'DRK'),
                        ('NVC', 'QRK'),
                        ('NVC', 'XPM'),
                        ('PPC', 'BTC'),
                        ('PPC', 'LTC'),
                        ('PPC', 'NVC'),
                        ('PPC', 'NMC'),
                        ('PPC', 'DRK'),
                        ('PPC', 'QRK'),
                        ('PPC', 'XPM'),
                        ('NMC', 'BTC'),
                        ('NMC', 'LTC'),
                        ('NMC', 'NVC'),
                        ('NMC', 'PPC'),
                        ('NMC', 'DRK'),
                        ('NMC', 'QRK'),
                        ('NMC', 'XPM'),
                        ('DRK', 'BTC'),
                        ('DRK', 'LTC'),
                        ('DRK', 'NVC'),
                        ('DRK', 'PPC'),
                        ('DRK', 'NMC'),
                        ('DRK', 'QRK'),
                        ('DRK', 'XPM'),
                        ('QRK', 'BTC'),
                        ('QRK', 'LTC'),
                        ('QRK', 'NVC'),
                        ('QRK', 'PPC'),
                        ('QRK', 'NMC'),
                        ('QRK', 'DRK'),
                        ('QRK', 'BTC'),
                        ('QRK', 'XPM'),
                        ('XPM', 'BTC'),
                        ('XPM', 'LTC'),
                        ('XPM', 'NVC'),
                        ('XPM', 'PPC'),
                        ('XPM', 'NMC'),
                        ('XPM', 'DRK'),
                        ('XPM', 'QRK'))

TOP_CURRENCIES = (('BTC', 'LTC'),
                    ('BTC', 'NVC'),
                    ('BTC', 'PPC'),
                    ('BTC', 'NMC'),
                    ('LTC', 'BTC'),
                    ('LTC', 'NVC'),
                    ('LTC', 'PPC'),
                    ('LTC', 'NMC'),
                    ('NVC', 'BTC'),
                    ('NVC', 'LTC'),
                    ('NVC', 'PPC'),
                    ('NVC', 'NMC'),
                    ('PPC', 'BTC'),
                    ('PPC', 'LTC'),
                    ('PPC', 'NVC'),
                    ('PPC', 'NMC'),
                    ('NMC', 'BTC'),
                    ('NMC', 'LTC'),
                    ('NMC', 'NVC'),
                    ('NMC', 'PPC'))

PAYPAL_CURRENCIES_FORM = [('EUR', 'EUR'),
                     ('USD', 'USD'),
                     ('JPY', 'JPY')]

PAYPAL_CURRENCIES = ['EUR','USD','JPY',]


DEFAULT_FEE = 1
FEE_PER_CURRENCIES = {'EUR': 4, 'USD':3, 'BTC':0.2, 'XPM':1,
                      'PPC':1, 'LTC':1, 'NMC':1, 'NVC':1, 'DRK':1,
                      'QRK':1}
DECIMAL_PER_CURRENCY = {'BTC': 0.000001, 'EUR': 0.01, 'USD':0.01, 'XPM': 0.0001}
DECIMAL_PER_CURRENCY_DEFAULT = 0.0001

MAX_PER_CURRENCY = {}
MAX_PER_CURRENCY_DEFAULT = 100000


DEFAULT_EXCHANGABLE_CURRENCIES = (('BTC', 'LTC'))
