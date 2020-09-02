from telegram.ext import Updater, CommandHandler
import requests
import time
import datetime as DT
from database import DBHelper
from matplotlib import pyplot as plt
import pandas as pd
import random
from config import CONFIG
import re
import os

CURRENCY_FROM = 0
AMOUNT_FROM = 1
CURRENCY_TO = -1
CURRENCY_PERIOD = 2
db = DBHelper(CONFIG["db_name"])


def get_list_url():
    r = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
    r.raise_for_status()
    content = r.json()
    return content['rates']


def get_history_url(period, symbols):
    today = DT.date.today()
    end_at = today.strftime("%Y-%m-%d")
    start_at = (today - DT.timedelta(days=period)).strftime("%Y-%m-%d")
    r = requests.get('https://api.exchangeratesapi.io/history?start_at={0}&end_at={1}&base=USD&symbols={2}'
                     .format(start_at, end_at, symbols.upper()))
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException:
        return None
    content = r.json()
    return {i: content['rates'][i] for i in sorted(content['rates'])}


def get_actual_rates(chat_id):
    history_rates = db.fetch_rates(chat_id=chat_id)
    if len(history_rates) > 0:
        print("Using rates from the database")
        return [rate for rate in history_rates[-1][0].split("\'") if rate != '[' and rate != ']' and rate != ', ']

    content = get_list_url()
    rates = ["●  {0}: {1}".format(rate, round(content[rate], 2)) for rate in content]
    db.insert_rates(chat_id, rates, time.time())
    return rates


def list_view(bot, update):
    chat_id = update.message.chat_id
    rates = get_actual_rates(chat_id)
    message = "\n".join(rates)
    bot.send_message(chat_id, text=message)
    return [chat_id, message]


def is_valid_exchange_params(params):
    return re.search(r'^(\$\d+ TO [A-Za-z]{3}$)|(^\d+ USD TO [A-Za-z]{3})$', ' '.join(params).upper())


def check_currency_name(currency_name):
    return currency_name.upper() in get_list_url()


def exchange_view(bot, update, args):
    chat_id = update.message.chat_id
    if not is_valid_exchange_params(args):
        bot.send_message(chat_id, "Invalid parameters")
        return

    rates = get_list_url()
    usd_value = float(args[CURRENCY_FROM]) if '$' not in args[CURRENCY_FROM] \
        else float(args[CURRENCY_FROM].replace('$', ''))
    need_currency = args[CURRENCY_TO].upper()
    if not check_currency_name(need_currency):
        bot.send_message(chat_id, text="Unknown currency")
        return

    result = rates[need_currency] * usd_value
    message = '{} {}'.format(round(result, 2), need_currency)
    bot.send_message(chat_id, text=message)


def build_chart(rates_and_period, currency):
    rate_list = [list(rates_and_period[rate].values())[0] for rate in rates_and_period]
    period_list = [period for period in rates_and_period]
    chart_directory = "charts"

    df = pd.DataFrame({'yvalues': rate_list, 'xvalues': period_list})
    plt.plot('xvalues', 'yvalues', data=df, marker='o')
    plt.title('rates USD/{0}'.format(currency.upper()))

    if not os.path.exists(chart_directory): os.makedirs(chart_directory)
    image_name = '{0}/{1}_{2}.png'.format(chart_directory, time.time(), random.random())
    plt.savefig(image_name)
    plt.close()
    return image_name


def is_valid_history_params(params):
    return re.search(r'^USD/[A-Z]{3} FOR \d+ DAYS', ' '.join(params).upper())


def history_view(bot, update, args):
    chat_id = update.message.chat_id
    if not is_valid_history_params(args):
        bot.send_message(chat_id, "Invalid parameters")
        return

    currency_name = args[CURRENCY_FROM].split('/')[CURRENCY_TO]

    if not check_currency_name(currency_name):
        bot.send_message(chat_id, text="Unknown currency")
        return

    currency_period = int(args[CURRENCY_PERIOD])
    result = get_history_url(currency_period, currency_name)
    if not result:
        bot.send_message(chat_id, text="No exchange rate data is available for the selected currency.")
        return

    chart = build_chart(result, currency_name)
    bot.send_photo(chat_id=chat_id, photo=open(chart, 'rb'))


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
