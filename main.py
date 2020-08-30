from telegram.ext import Updater, CommandHandler
import requests
import time
import datetime as DT
from database import DBHelper
from matplotlib import pyplot as plt
import pandas as pd
import random
from config import CONFIG

db = DBHelper(CONFIG["db_name"])


def get_list_url():
    contents = requests.get('https://api.exchangeratesapi.io/latest?base=USD').json()
    return contents['rates']


def get_history_url(period, symbols):
    today = DT.date.today()
    end_at = today.strftime("%Y-%m-%d")
    start_at = (today - DT.timedelta(days=period)).strftime("%Y-%m-%d")
    r = requests.get('https://api.exchangeratesapi.io/history?start_at={0}&end_at={1}&base=USD&symbols={2}'
                     .format(start_at, end_at, symbols.upper()))
    r.raise_for_status()
    content = r.json()
    return {i: content['rates'][i] for i in sorted(content['rates'])}


def list_view(bot, update):
    chat_id = update.message.chat_id
    history_rates = db.fetch_rates(chat_id=chat_id)
    if len(history_rates) > 0:

        rates = [rate for rate in history_rates[-1][0].split("\'") if rate != '[' and rate != ']' and rate != ', ']
        print("Use rate from DB")
    else:
        content = get_list_url()
        rates = ["●  {0}: {1}".format(rate, round(content[rate], 2)) for rate in content]
        print("Use rate from url")
    db.insert_rates(chat_id, rates, time.time())

    bot.send_message(chat_id, text=("\n".join(rates)))


def exchange_view(bot, update, args):
    chat_id = update.message.chat_id
    if (len(args) == 3 or len(args) == 4) and 'to' in args:
        usd_value = args[0] if '$' not in args[0] else args[0].replace('$', '')
        try:
            usd_value = float(usd_value)
        except ValueError:
            bot.send_message(chat_id, text="USD value not valid")
            return
        if len(args) == 4 and args[1].upper() != 'USD':
            bot.send_message(chat_id, text="Wrong currency to exchange")
            return
        need_currency = args[-1].upper()
        rates = get_list_url()
        if need_currency not in rates:
            message = "The required currency is not in the list"
        else:
            value_need_currency = rates[need_currency] * usd_value
            message = str(round(value_need_currency, 2)) + ' ' + need_currency
    else:
        message = "Invalid parameters"

    bot.send_message(chat_id, text=message)


def build_chart(rates_and_period, currency):
    rates = [list(rates_and_period[rate].values())[0] for rate in rates_and_period]
    periods = [period for period in rates_and_period]

    df = pd.DataFrame({'yvalues': rates, 'xvalues': periods})
    plt.plot('xvalues', 'yvalues', data=df, marker='o')
    plt.title('rates USD/{0}'.format(currency.upper()))

    image_name = 'charts/{0}_{1}.png'.format(time.time(), random.random())
    plt.savefig(image_name)
    plt.close()
    return image_name


def history_view(bot, update, args):
    chat_id = update.message.chat_id
    if len(args) == 4 and 'for' in args[1] and 'days' in args[3]:
        currencys = args[0].split('/')
        if len(currencys) != 2:
            bot.send_message(chat_id, text="There must be 2 currencies")
            return
        rates = get_list_url()

        if currencys[1].upper() not in rates or currencys[0].upper() != 'USD':
            bot.send_message(chat_id, text="The required currency is not in the list")
            return
        try:
            period = int(args[2])
        except ValueError:
            bot.send_message(chat_id, text="Period not valid")
            return
        rates = get_history_url(period, currencys[1])
        if rates == "empty":
            bot.send_message(chat_id, text="No exchange rate data is available for the selected currency.")
            return
        chart = build_chart(rates, currencys[1])
        print(chart)
        bot.send_photo(chat_id=chat_id, photo=open(chart, 'rb'))
    else:
        bot.send_message(chat_id, text="Invalid parameters")


def main():
    db.setup()
    updater = Updater(CONFIG["bot_token"])
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('list', list_view))
    dp.add_handler(CommandHandler('exchange', exchange_view, pass_args=True))
    dp.add_handler(CommandHandler('history', history_view, pass_args=True))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
