"""Telegram Currency Bot (SF)"""

from confmaker import config
from extensions import Converter, ConvertError, NetworkFetchError, logger
import telebot
import re
import sys

messages = {
    'start': 'Hello, {name}!\n\n'
             'Thank for choosing Currency Converter bot!\n\n'
             'Available commands:\n'
             '/start\n'
             '/help\n'
             '/values\n'
             '/about\n',
    'help': 'Exchange rate: USD/CHF\n'
            'Conversion: 20 EUR/BTC',
    'values': 'Supported fiat: USD, EUR, GBP, CHF, RUB\n'
              'Supported crypto: BTC, ETH, LTC, DOGE\n\n'
              'Full list: https://coingate.com/supported-currencies',
    'about': '@m0nochr0me \n C5.6 INTPY-1 07.2022'
}

# Create bot
if not config['token']:
    print('Setup token in config.toml!')
    logger.error('No configured token')
    sys.exit(0)

bot = telebot.TeleBot(config['token'], parse_mode=None)


# Register handlers
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, messages['start'].format(name=message.from_user.first_name))
    logger.info(f'Received /start from {message.from_user}')


@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.reply_to(message, messages['help'])
    logger.info(f'Received /help from {message.from_user}')


@bot.message_handler(commands=['values'])
def send_welcome(message):
    bot.reply_to(message, messages['values'])
    logger.info(f'Received /values from {message.from_user}')


@bot.message_handler(commands=['about'])
def send_welcome(message):
    bot.reply_to(message, messages['about'])
    logger.info(f'Received /about from {message.from_user}')


@bot.message_handler(content_types=['text'])
def conv(message):
    logger.debug(message.text)
    # Split input not only by space but also by: / \ , | and newline
    # make list excluding empty elements
    symbols = [s for s in re.split(r'[\s*|\n,/]', message.text) if s]

    # If only two symbols and no amount, assume user wanted just exchange rate
    if len(symbols) <= 2:
        symbols = [1.0] + symbols

    try:
        rate = Converter.get_conv(*symbols)
    except ConvertError as e:
        logger.error(f'Convertion Error -- {e}')
        reply = 'Unable to convert'
    except NetworkFetchError as e:
        logger.error(f'Remote API failure -- {e}')
        reply = 'Remote API failure'
    except ValueError as e:
        logger.error(f'Invalid amount -- {e}')
        reply = 'Invalid amount'
    except Exception as e:
        logger.error(f'Unknown error -- {e}')
        reply = 'Unknown error'
    else:
        reply = f'{rate}'
        logger.debug(f'Conv rate: {reply}')

    bot.reply_to(message, reply)
    logger.info(f'Received conversion request from {message.from_user.username}')


if __name__ == '__main__':
    logger.info('CurrencyBot Start')
    bot.infinity_polling()
