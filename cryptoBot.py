import robin_stocks.robinhood as r
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from datetime import datetime as dt
import time

dollar = 0
ticker = 'NONE'
calc = False
fetch = False
order = False
orderPrice = 0
close = 0

dt.now()
exchange = ccxt.binance()

f = open("login.txt", "r")
f = f.readline()
login = f.split(':')
login = r.login(login[0],login[1])

def toString(num):
  x = np.float64(num)
  y = x.item()
  return y



def getPos(ticker):
  limit = 210     
  bars = exchange.fetch_ohlcv(ticker , timeframe='5m' , limit=210)
  df = pd.DataFrame(bars, columns=['time','high', 'low', 'open','close', 'volume'])
  rsi = ta.rsi(df['close'])
  adx = ta.adx(df['high'], df['low'], df['close'])
  ao = ta.ao(df['high'], df['low'])
  ema5 = ta.ema(df['close'], length=5)
  ema21 = ta.ema(df['close'], length=21)
  ema50 = ta.ema(df['close'], length=50)
  ema200 = ta.ema(df['close'], length=200)
  bbands = ta.bbands(df['close'])
  df = pd.concat([df, rsi, adx, ao, ema5, ema21, ema50, ema200, bbands], axis=1)
  recentData = df.iloc[-1]
  close = recentData['close']
  lower = recentData['BBL_5_2.0']
  upper = recentData['BBU_5_2.0']
  bbPercent = (close - lower)/(upper - lower)
  global fetch
  if fetch == False:
    print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[██   ]: FETCHING RECENT DATA')
    fetch = True
  ptrade = 0
  if recentData['EMA_50'] > recentData['EMA_200']:
    ptrade += 1
  if recentData['EMA_5'] > recentData['EMA_21']:
    ptrade += 1
  if bbPercent >= 0.75:
    ptrade += 1
  if recentData['ADX_14'] >= 15:
    ptrade += 1
  if ao[limit-1] >= 0.25:
    ptrade += 1
  ticker = ticker[:3]
  robinTicker = ticker[:3]
  global calc
  if calc == False:
    print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[███  ]: WAITING FOR INDICATOR ALIGNMENT - BE PATIENT')
    calc = True
  if ptrade >= 5:
    r.orders.order_buy_crypto_by_price(robinTicker, dollar, timeInForce='gtc', jsonify=False)
    global orderPrice
    orderPrice = int(toString(close))
    print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[████ ]: PLACED ORDER')
    global order
    order = True
    print(f"""
    ╔═══════════════════════════════════════════════════════╗        
     TICKER: {robinTicker} \n                              
     DOLLAR AMOUNT: {dollar} \n 
     BOUGHT PRICE: {toString(close)} \n       
     PROFIT: {toString(close) * 1.01} \n                   
     STOP LOSS: {toString(close) * 0.98} \n                
     TIME IN FORCE: GOOD TILL CANCEL \n                                       
    ╚═══════════════════════════════════════════════════════╝
    """)
    return order
  else:
    order = False
    return order



def check(ticker):
  robinTicker = ticker[:3]
  portfolio = r.get_crypto_positions()
  df = pd.DataFrame(portfolio)
  df = df['quantity']
  if ticker == "LTC/USDT":
    quantity = df[0]
  if ticker == "DOGE/BTC":
    quantity = df[1] 
  if ticker == "ETH/USDT":
    quantity = df[2] 
  if ticker == "BTC/USDT":
    quantity = df[3] 
  while True:
    if dt.now().second % 5 == 0: 
      print("checking")
      bars = exchange.fetch_ohlcv(ticker , timeframe='1m' , limit=1)
      df = pd.DataFrame(bars, columns=['time','high', 'low', 'open','close', 'volume'])
      recentData = df.iloc[-1]
      curPrice= recentData['close']
      if int(toString(curPrice)) <= (orderPrice*0.98):
        r.orders.order_sell_crypto_by_quantity(ticker[:3], quantity, timeInForce='gtc', jsonify=False)
        print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[█████]: CLOSED POSITION (SL TRIGGERED)')
        print(f"""
        ╔═══════════════════════════════════════════════════════╗        
        Ticker: {robinTicker} \n                                              
        STOP LOSS: {toString(close) * 0.98} \n                
        TIME IN FORCE: GOOD TILL CANCEL \n                                    
        ╚═══════════════════════════════════════════════════════╝
        """)

        time.sleep(10)
        return False
      if int(toString(curPrice)) >= (orderPrice*1.01):
        r.orders.order_sell_crypto_by_quantity(ticker[:3], quantity, timeInForce='gtc', jsonify=False)
        print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[█████]: CLOSED POSITION (P TRIGGERED)')
        print(f"""
        ╔═══════════════════════════════════════════════════════╗        
        TICKER: {robinTicker} \n                                              
        PROFIT: {toString(close) * 1.01} \n                
        TIME IN FORCE: GOOD TILL CANCEL \n                          
        ╚═══════════════════════════════════════════════════════╝
        """)

        time.sleep(10)
        return False

def main():
  print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} \t[█    ]: STARTING MAIN')
  while True:
    if dt.now().minute % 5 == 0 or dt.now().minute == 0:
      order1 = False
      print(order1)
      while True:
        if order1 == False:
          print('getpos')
          order1 = getPos(ticker)
          time.sleep(30)
        if order1 == True:
          print(f"{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second}check")
          order1 = check(ticker)
    else:
      time.sleep(2)

print("""
████████╗██████╗░░█████╗░██████╗░███████╗  ███╗░░░███╗░█████╗░██╗░░██╗███████╗██████╗░░██████╗
╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔════╝  ████╗░████║██╔══██╗██║░██╔╝██╔════╝██╔══██╗██╔════╝
░░░██║░░░██████╔╝███████║██║░░██║█████╗░░  ██╔████╔██║███████║█████═╝░█████╗░░██████╔╝╚█████╗░
░░░██║░░░██╔══██╗██╔══██║██║░░██║██╔══╝░░  ██║╚██╔╝██║██╔══██║██╔═██╗░██╔══╝░░██╔══██╗░╚═══██╗
░░░██║░░░██║░░██║██║░░██║██████╔╝███████╗  ██║░╚═╝░██║██║░░██║██║░╚██╗███████╗██║░░██║██████╔╝
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░╚══════╝  ╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚═════╝░
""")

validD = False
validT = False
while validT == False and validD == False:
  validT = False
  validD = False
  while validT == False:
    ticker = input(f"""{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} What ticker would you like?
      0: LTC
      1: BTC
      2: ETH
      3: NULL
    """)
    if ticker == '0':
      ticker = 'LTC/USDT'
      validT = True
    elif ticker == '1':
      ticker = 'BTC/USDT'
      validT = True
    elif ticker == '2':
      ticker = 'ETH/USDT'
      validT = True
    elif ticker == '3':
      ticker = ''
      validT = True
    else: 
      print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} ERROR: TICKER INVALID')
  dollar = input(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} How many dollars are you willing to invest?: ')
  print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} Read Command: will send message if long or short opportunity arises! Waiting for time alignment\n. ')
  try:
    dollar = float(dollar)
    validD = True
  except:
    print(f'{dt.now().hour + 5}:{dt.now().minute}:{dt.now().second} ERROR: DOLLAR AMOUNT INVALID (INPUT FLOAT)')


# runs code
main()


