import robin_stocks.robinhood as r
import os
import robin_stocks.robinhood as r
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime as dt
import time

f = open("login.txt", "r")
f = f.readline()
login = f.split(':')
login = r.login(login[0],login[1])

portfolio = r.get_crypto_positions()
df = pd.DataFrame(portfolio)
print(df['account_id'])
print(df['created_at'])
print(df['currency'])
print(df['id'])
print(df['quantity'])
print(df['quantity_available'])
print(df['quantity_held_for_buy'])
print(df['quantity_held_for_sell'])
print(df['updated_at'])
df = df['quantity']
print(df[0])
print(df[1])
print(df[2])
print(df[3])



#try:
#  r.orders.order_sell_crypto_by_quantity('ETH', df[2], timeInForce='gtc', jsonify=False)
#  print('sucess')
#except:
#  print('FAILLL NOOOOB')
