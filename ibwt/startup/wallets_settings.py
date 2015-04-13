# -*- coding: utf-8 -*-
# WALLETS CONNECTION
# DEFINE FOR EVERY CRYPTOCURRENCY
# ITS CREDENTIAL TO ACCESS TO WALLET

import pyjsonrpc

BTC_CONF_FILE='PATH/TO/CONF'
BTC_NETWORK = 'testnet'
BTC_URL = 'URL:PORT'
BTC_USERNAME = 'YOUR_USERNAME'
BTC_PASSWORD = 'YOUR_PASSWORD'
BTC_ACCOUNT = 'YOUR_ACCOUNT'
# Litecoin
LTC_CONF_FILE='PATH/TO/CONF'
LTC_NETWORK = 'testnet' # only in test
LTC_URL = 'URL:PORT'
LTC_USERNAME = 'YOUR_USERNAME'
LTC_PASSWORD = 'YOUR_PASSWORD'
LTC_ACCOUNT = 'YOUR_ACCOUNT'

# Quarkcoin
QRK_CONF_FILE='PATH/TO/CONF'
QRK_NETWORK = 'testnet' # only in test
QRK_URL = 'URL:PORT'
QRK_USERNAME = 'YOUR_USERNAME'
QRK_PASSWORD = "YOUR_PASSWORD"
QRK_ACCOUNT = 'YOUR_ACCOUNT'

# Darkcoin
DRK_CONF_FILE='PATH/TO/CONF'
DRK_NETWORK = 'testnet' # only in test
DRK_URL = 'URL:PORT'
DRK_USERNAME = 'YOUR_USERNAME'
DRK_PASSWORD = "YOUR_PASSWORD"
DRK_ACCOUNT = 'YOUR_ACCOUNT'

# Namecoin
NMC_CONF_FILE='/home/bitcoinuser/.namecoin/namecoin.conf'
NMC_NETWORK = 'testnet' # only in test
NMC_URL = 'URL:PORT'
NMC_USERNAME = 'YOUR_USERNAME'
NMC_PASSWORD = "YOUR_PASSWORD"
NMC_ACCOUNT = 'YOUR_ACCOUNT'

# Novacoin
NVC_CONF_FILE='/home/bitcoinuser/.novacoin/novacoin.conf'
NVC_NETWORK = 'testnet' # only in test
NVC_URL = 'URL:PORT'
NVC_USERNAME = 'YOUR_USERNAME'
NVC_PASSWORD = "YOUR_PASSWORD"
NVC_ACCOUNT = 'YOUR_ACCOUNT'


# PPC
PPC_CONF_FILE='/home/bitcoinuser/.ppcoin/ppcoin.conf'
PPC_URL = 'URL:PORT'
PPC_USERNAME = 'YOUR_USERNAME'
PPC_PASSWORD = "YOUR_PASSWORD"
PPC_ACCOUNT = 'YOUR_ACCOUNT'


btc_client = pyjsonrpc.HttpClient(
    url = BTC_URL,
    username = BTC_USERNAME,
    password = BTC_PASSWORD
)

ltc_client = pyjsonrpc.HttpClient(
    url = LTC_URL,
    username = LTC_USERNAME,
    password = LTC_PASSWORD
)

qrk_client = pyjsonrpc.HttpClient(
    url = QRK_URL,
    username = QRK_USERNAME,
    password = QRK_PASSWORD
)

drk_client = pyjsonrpc.HttpClient(
    url = DRK_URL,
    username = DRK_USERNAME,
    password = DRK_PASSWORD
)

nvc_client = pyjsonrpc.HttpClient(
    url = NVC_URL,
    username = NVC_USERNAME,
    password = NVC_PASSWORD
)

nmc_client = pyjsonrpc.HttpClient(
    url = NMC_URL,
    username = NMC_USERNAME,
    password = NMC_PASSWORD
)

ppc_client = pyjsonrpc.HttpClient(
    url = PPC_URL,
    username = PPC_USERNAME,
    password = PPC_PASSWORD
)
