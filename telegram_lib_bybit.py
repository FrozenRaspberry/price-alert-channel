import telegram
from telegram import Update
from telegram.ext import filters, MessageHandler, ContextTypes
from keys_bybit import *
import time

if (need_proxy):
	pp = telegram.utils.request.Request(proxy_url='https://127.0.0.1:7890')
	bot = telegram.Bot(token=tg_api_key, request=pp)
else:
	bot = telegram.Bot(token=tg_api_key)

def sendMessage(msg, log = True, test = False):
	if log:
		print('Send msg: ' + msg)
	if not test:
		try:
			bot.send_message(chat_id, text=msg)
		except Exception as e:
			errMsg = '!Send Message error ' + str(e)
			print('BYBIT BOT发送消息时发生错误\n', errMsg)
			sendAdminMessage('BYBIT BOT发送消息时发生错误\n' + errMsg)
			sendAdminMessage('Sleep 60s')
			time.sleep(60)

def sendAdminMessage(msg, log = True, test = False):
	if log:
		print('Send msg: ' + msg)
	if not test:
		try:
			bot.send_message(admin_id, text=msg)
		except Exception as e:
			print('Send Admin Message Error ', msg)
			exit()