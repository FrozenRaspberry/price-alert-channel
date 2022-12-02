import hmac
import base64
import requests
import json
import time
import datetime
from telegram_lib_bybit import *
from keys_bybit import *

tgTestMode = False
sendAdminMessage('Bybit Price Alert Channel Bot Start', test = tgTestMode)
lastMessageId = 0

if (need_proxy):
	proxies = {'https': 'http://127.0.0.1:7890'}
else:
	proxies = {}

def get_time():
	now = datetime.datetime.utcnow()
	t = now.isoformat("T", "milliseconds")
	return t + "Z"

def signature(timestamp, method, request_path, body,secret_key):
	if str(body) == '{}' or str(body) == 'None':
		body = ''
	message = str(timestamp) + str.upper(method) + request_path + str(body)
	mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
	d = mac.digest()
	return base64.b64encode(d)

def get_header(endpoint):
	body= {}
	request= 'GET'
	header = dict()
	header['CONTENT-TYPE'] = 'application/json'
	# header['OK-ACCESS-KEY'] = bybit_api_key
	current_time = get_time()
	# header['OK-ACCESS-SIGN'] = signature(current_time, request, endpoint , body, okx_api_secret)
	# header['OK-ACCESS-TIMESTAMP'] = str(current_time)
	# header['OK-ACCESS-PASSPHRASE'] = okx_api_pass
	return header

#最新订单数据
def GetTickers():
	tickers = {}
	endpoint= '/derivatives/v3/public/tickers?category=linear'
	url = bybit_base_url + endpoint
	headers = get_header(endpoint)
	try:
		r = requests.get(url, headers=headers, proxies=proxies)
		r_data = r.json()
		if (r_data['retCode'] == 0):
			for t in r_data['result']['list']:
				tickers[t['symbol']] = t
			return tickers
		else:
			return None
	except Exception as e:
		print('!Get Ticker Error: ', e)
		sendAdminMessage('!Get Ticker Error: ', e)
		return None
	return pdOrders

def CheckTickers(newTickers):
	for symbol in newTickers:
		t = newTickers[symbol]
		lastPrice = float(t['lastPrice'])
		openPrice = float(t['prevPrice24h'])
		# print(t['symbol'], openPrice, lastPrice)
		if (lastPrice) / openPrice > 1.05 or lastPrice / openPrice < 0.95:
			if tickerRecorded.get(t['symbol']) is None:
				sendMessage(time.strftime('%H:%M:%S') + ' ' + t['symbol'] + ' 目前变化幅度为 ' + str(round(((lastPrice-openPrice)/openPrice*100),2)) + '%  现价' + str(lastPrice) + '  原价' + str(openPrice),test = tgTestMode)
				tickerRecorded[t['symbol']] = lastPrice / openPrice
			else:
				if lastPrice / openPrice > 1.05 and lastPrice / openPrice - tickerRecorded[t['symbol']] > 0.005:
					sendMessage(time.strftime('%H:%M:%S') + ' ' + t['symbol'] + ' 目前变化幅度为 ' + str(round(((lastPrice-openPrice)/openPrice*100),2)) + '%  现价' + str(lastPrice) + '  原价' + str(openPrice),test = tgTestMode)
					tickerRecorded[t['symbol']] = lastPrice / openPrice
				elif lastPrice / openPrice < 0.95 and lastPrice / openPrice - tickerRecorded[t['symbol']] < -0.005:
					sendMessage(time.strftime('%H:%M:%S') + ' ' + t['symbol'] + ' 目前变化幅度为 ' + str(round(((lastPrice-openPrice)/openPrice*100),2)) + '%  现价' + str(lastPrice) + '  原价' + str(openPrice),test = tgTestMode)
					tickerRecorded[t['symbol']] = lastPrice / openPrice

# if not tgTestMode:
# 	lastMessageId = bot.get_updates()[-1].message.message_id
# 	print('init msg id' + str(lastMessageId))

# 初始化变量
tickerRecorded = {}
tickCount = 0
lastClearDay = datetime.date.today().day
while True:
	newTickers = GetTickers()
	if newTickers is None:
		print('Get ticker failed, retry.')
		continue
	CheckTickers(newTickers)
	# print('----------------------',tickCount)
	time.sleep(2)
	today = datetime.date.today().day
	if today != lastClearDay:
		sendMessage(time.strftime('%H:%M:%S') + ' 0点已过，清空数据', test = tgTestMode)
		lastClearDay = today
		tickerRecorded = {}
	tickCount += 1
