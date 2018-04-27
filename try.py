from binance.client import Client
import time
import datetime

api_key = "SizUjhBcA2eT7AdZhF7hLny5fNtKEW5estbhasjB8HODboIqmky3g9iSO2KiXDeJ"
api_secret = "I1OnxPHtPVHxHRcUs01LYRqasxO998v21n0n8nT0g2vaHZWeVfMwNWRnaNTmAlk2"

client = Client(api_key, api_secret)

PRICE_PERCENTAGE_CHANGE = 1.25
VOLUME_PERCENTAGE_CHANGE = 0.2

def load_top100():
    return [ticker.strip()  for ticker in [
        'BTC',
        'ETH',
        'XRP',
        'BCC',
        'EOS',
        'LTC',
        'ADA',
        'XLM',
        'MIOTA',
        'NEO',
        'TRX',
        'XMR',
        'DASH',
        'XEM',
        'USDT',
        'ETC',
        'VEN',
        'OMG',
        'QTUM',
        'BNB',
        'ICX',
        'BTG',
        'LSK',
        'ZEC',
        'XVG',
        'BCN',
        'STEEM',
        'NANO',
        'BTM',
        'BTCP',
        'SC',
        'PPT',
        'WAN',
        'BCD',
        'BTS',
        'ZIL',
        'DOGE',
        'MKR',
        'STRAT',
        'ONT',
        'AE',
        'DCR',
        'ZRX',
        'WAVES',
        'DGD',
        'XIN',
        'RHOC',
        'SNT',
        'AION',
        'REP',
        'HSR',
        'GNT',
        'LRC',
        'IOST',
        'WTC',
        'BAT',
        'DGB',
        'KMD',
        'ARDR',
        'ARK',
        'KNC',
        'MITH',
        'KCS',
        'CENNZ',
        'MONA',
        'PIVX',
        'SUB',
        'DRGN',
        'SYS',
        'DCN',
        'ELF',
        'CNX',
        'GAS',
        'QASH',
        'ETHOS',
        'STORM',
        'NPXS',
        'FCT',
        'NAS',
        'CTXC',
        'VERI',
        'BNT',
        'RDD',
        'WAX',
        'ELA',
        'GXS',
        'FUN',
        'SALT',
        'XZC',
        'NXT',
        'POWR',
        'KIN',
        'ENG',
        'MCO',
        'GTO',
        'R',
        'NCASH',
        'GBYTE',
        'ETN',
        'MAID'
    ]]

def report_ticker_info(ticker, last_info, now_info, addition):

    now_price = 0.0
    now_quoteVolume = 0.0
    now_volume = 0.0
    last_price = 0.0
    lastquoteVolume = 0.0
    lastVolume = 0.0

    found = False
    for now in now_info:
        if now["symbol"] == ticker + addition:
            now_price = now["lastPrice"]
            now_quoteVolume = now["quoteVolume"]
            now_volume = now["volume"]
            found = True
            break
    if not found:
        return
    found = False
    for last in last_info:
        if last["symbol"] == ticker + addition:
            last_price = last["lastPrice"]
            last_quoteVolume = last["quoteVolume"]
            last_Volume = last["volume"]
            found = True
            break
    if not found:
        return

    # if ticker == "BTC":
    #     print(str(datetime.datetime.now()) + " ... JUST!")
    #     print("Last: " + str(last))
    #     print("Now: " + str(now))

    if (float(now_price) > (float(last_price)*((PRICE_PERCENTAGE_CHANGE + 100)/100)) and
            (float(now_quoteVolume) > (float(last_quoteVolume) * ((VOLUME_PERCENTAGE_CHANGE + 100) / 100)))):
        print(str(datetime.datetime.now()) + "**** UP!")
        print("Last: " + str(last))
        print("Now: " + str(now))
    elif (float(now_price) < (float(last_price)*((100 - PRICE_PERCENTAGE_CHANGE)/100)) and
            (float(now_quoteVolume) > (float(last_quoteVolume) * ((VOLUME_PERCENTAGE_CHANGE + 100) / 100)))):
        print(str(datetime.datetime.now()) + "**** DOWN!")
        print("Last: " + str(last))
        print("Now: " + str(now))


# get market depth
tickers = load_top100()
millis1 = int(round(time.time() * 1000))
last_info = client.get_ticker()
while True:
    print("Wait..")
    time.sleep(60)
    now_info = client.get_ticker()

    for ticker in tickers:
        addition = "USDT" if ticker == "BTC" else "BTC"
        report_ticker_info(ticker, last_info, now_info, addition)

    last_info = now_info







