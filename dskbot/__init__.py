import logging
from os import getenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .yuan import yuan_exchange_rate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init():
    token = getenv('TELEGRAM_TOKEN')
    app = Application.builder() \
        .token(token) \
        .build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', start))
    app.add_handler(CallbackQueryHandler(button))
    return app


async def start(update: Update, *_):
    ''' Send a message when the command /start is issued. '''
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(text='¥ Курс Юаня', callback_data='yuan')],
        [InlineKeyboardButton(text='🛠 Поддержка', callback_data='support')],
        [InlineKeyboardButton(text='🛍 Магазин', url='https://www.google.com')],
        [InlineKeyboardButton(text='📊 Отзывы', url='https://www.google.com')],
    ])
    await update.message.reply_text("Привет! Я бот пчёлка🐝", reply_markup=reply_markup)


async def button(update: Update, *_):
    ''' Parses the button. '''
    query = update.callback_query
    match query.data:
        case 'yuan':
            rate = yuan_exchange_rate()
            await query.message.reply_text(f'Текущий курс рубля к юаню: 1¥ = {rate}₽')
        case 'support':
            await query.message.reply_text('У вас есть вопрос или проблема? Можете написать в нашу поддержку @dsk_support')
