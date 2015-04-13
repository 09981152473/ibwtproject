# -*- coding: utf-8 -*-
# WALLETS CONNECTION
# Bitcoin
import pyjsonrpc

BTC_CONF_FILE='/home/bitcoinuser/.bitcoin/bitcoin.conf'
BTC_NETWORK = 'testnet'
BTC_URL = 'http://127.0.0.1:8332'
BTC_USERNAME = 'bitcoinuser'
BTC_PASSWORD = 'ndifanci35nci240nxi40ntc30n6c24i0n54i20nx4n20'
BTC_ACCOUNT = 'IBWT_BANK'
# Litecoin
LTC_CONF_FILE='/home/bitcoinuser/.litecoin/litecoin.conf'
LTC_NETWORK = 'testnet'
LTC_URL = 'http://127.0.0.1:9332'
LTC_USERNAME = 'litecoinuser'
LTC_PASSWORD = 'ndadghdhgadgH*thaec24i0n54i20nx4n20'
LTC_ACCOUNT = 'IBWT_BANK'

# Quarkcoin
QRK_CONF_FILE='/home/bitcoinuser/.quarkcoin/quarkcoin.conf'
QRK_NETWORK = 'testnet'
QRK_URL = 'http://127.0.0.1:10332'
QRK_USERNAME = 'quarkcoinuser'
QRK_PASSWORD = "nsfghf£$HFRFSGHnfhgVsgvtwrRWT0nx4n20"
QRK_ACCOUNT = 'IBWT_BANK'

# Darkcoin
DRK_CONF_FILE='/home/bitcoinuser/.darkcoin/darkcoin.conf'
DRK_NETWORK = 'testnet'
DRK_URL = 'http://127.0.0.1:11332'
DRK_USERNAME = 'darkcoinuser'
DRK_PASSWORD = "ndsgi426nfi42x0i4n250xi4n0iv6n245"
DRK_ACCOUNT = 'IBWT_BANK'

# Namecoin
NMC_CONF_FILE='/home/bitcoinuser/.namecoin/namecoin.conf'
NMC_NETWORK = 'testnet'
NMC_URL = 'http://127.0.0.1:14332'
NMC_USERNAME = 'namecoinuser'
NMC_PASSWORD = "dan9c29nx084b6v024nx9zn9Dgfc6429v42kmn"
NMC_ACCOUNT = 'IBWT_BANK'

# Novacoin
NVC_CONF_FILE='/home/bitcoinuser/.novacoin/novacoin.conf'
NVC_NETWORK = 'testnet'
NVC_URL = 'http://127.0.0.1:12332'
NVC_USERNAME = 'darkcoinuser'
NVC_PASSWORD = "afndsgtocn4tonvonwatovc243to2n4x"
NVC_ACCOUNT = 'IBWT_BANK'


# PPC
PPC_CONF_FILE='/home/bitcoinuser/.ppcoin/ppcoin.conf'
PPC_URL = 'http://127.0.0.1:13332'
PPC_USERNAME = 'ppcoinuser'
PPC_PASSWORD = "abc4bcu4b60b20x48b5c0842b580bv085b2405n2094kx0n2"
PPC_ACCOUNT = 'IBWT_BANK'


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