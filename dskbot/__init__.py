import logging
from os import getenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from .yuan import yuan_exchange_rate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
token = getenv('TELEGRAM_TOKEN')
channel_name = '@dsk_ch'
comission = 300

CALCULATE_START = 1
CALCULATE_COUNT = 2
CALCULATE_TOTAL = 3


def init():
    app = Application.builder() \
        .token(token) \
        .build()

    app.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler(('start', 'help'), start),
            CallbackQueryHandler(order, pattern='order'),
            CallbackQueryHandler(calculate, pattern='calculate'),
        ],
        states={
            CALCULATE_START: [CallbackQueryHandler(calculate_start)],
            CALCULATE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_count)],
            CALCULATE_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_total)],
        },
        fallbacks=[CommandHandler(('start', 'cancel'), start)],
    ))

    return app


async def start(update: Update, _):
    ''' Send a message when the command /start is issued. '''
    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text='🛍 Магазин', url='https://docs.google.com/spreadsheets/d/11r7_7HVRW-cU_t93-BB68Qsn2GbQQEfvwkkVkZQsfuE/edit#gid=0'),
            InlineKeyboardButton(text='📊 Отзывы', url='https://t.me/dsk_reviews/1'),
        ],
        [
            InlineKeyboardButton(text='🔥 Сделать заказ', callback_data='order'),
        ],
        [
            InlineKeyboardButton(text='🧮 Рассчитать стоимость доставки', callback_data='calculate'),
        ],
    ])
    text = f'Привет! Я бот пчёлка 🐝\n\nТекущий курс рубля к юаню: 1¥ = {yuan_exchange_rate()}₽'
    await update.message.reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END


async def order(update: Update, _):
    await update.callback_query.message.reply_text('Чтобы сделать заказ напишите @dsk_support')


async def calculate(update: Update, _):
    await update.callback_query.message.reply_text('Выберите категорию:', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='👟 Обувь', callback_data='1400')],
        [InlineKeyboardButton(text='👕 Одежда', callback_data='600')],
        [InlineKeyboardButton(text='🎒 Аксессуары', callback_data='700')],
    ]))
    return CALCULATE_START


async def calculate_start(update: Update, context):
    context.user_data['shipping'] = int(update.callback_query.data)
    await update.callback_query.message.reply_text('Введите количество товара:')
    return CALCULATE_COUNT


async def calculate_count(update: Update, context):
    try:
        count = int(update.message.text)
    except Exception:
        await update.message.reply_text('Не удалось прочитать количество товара.\nПожалуйста, введите количество товара:')
        return CALCULATE_COUNT

    context.user_data['count'] = count
    await update.message.reply_text('Введите общую сумму заказа в юанях:')
    return CALCULATE_TOTAL


async def calculate_total(update: Update, context):
    try:
        amount = round((float(update.message.text)+50) * yuan_exchange_rate(), 0)
    except Exception:
        await update.message.reply_text('Не удалось прочитать общую сумму заказа.\nПожалуйста, введите общую сумму заказа в юанях:')
        return CALCULATE_TOTAL

    shipping = context.user_data['shipping']
    comission_total = context.user_data['count'] * comission
    text = f'Стоимость заказа: {amount}₽\n'
    text += f'Доставка: {shipping}₽\n'
    text += f'----------------------\n'
    text += f'<b>ИТОГО: {amount + shipping+comission_total}₽</b>\n\n'
    await update.message.reply_text(text, parse_mode='html')
    return await start(update, context)
