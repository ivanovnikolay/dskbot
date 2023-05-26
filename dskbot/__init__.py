import logging
from os import getenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,Bot, ChatMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from .yuan import yuan_exchange_rate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
token = getenv('TELEGRAM_TOKEN')
channel_name = '@dsk_ch'


def init():
    app = Application.builder() \
        .token(token) \
        .build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', start))
    app.add_handler(CallbackQueryHandler(button))
    return app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ''' Send a message when the command /start is issued. '''
    user_id = update.effective_user.id
    subscribed = await is_subscribed(context.bot, user_id)
    if subscribed:
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text='🔥 Сделать заказ', callback_data='order'),
                InlineKeyboardButton(text='¥ Курс Юаня', callback_data='yuan'),
            ],
            [
                InlineKeyboardButton(text='🛍 Магазин', callback_data='shop'),
                InlineKeyboardButton(text='📊 Отзывы', callback_data='feedback'),
            ],
            [
                InlineKeyboardButton(text='🧮 Рассчитать стоимость доставки', callback_data='calc'),
            ],
        ])
        await update.message.reply_text('Привет! Я бот пчёлка 🐝', reply_markup=reply_markup)
    else:
        await update.message.reply_text(f'Вы не подписаны на канал. Пожалуйста, подпишитесь на канал {channel_name} и повторите попытку.')


async def is_subscribed(bot, user_id):
    try:
        member = await bot.get_chat_member(channel_name, user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except Exception:
        return True  # ignore errors


async def button(update: Update, *_):
    ''' Parses the button. '''
    query = update.callback_query
    match query.data:
        case 'order':
            await query.message.reply_text('Чтобы сделать заказ напишите @dsk_support')
        case 'yuan':
            rate = yuan_exchange_rate()
            await query.message.reply_text(f'Текущий курс рубля к юаню: 1¥ = {rate}₽')
        case 'shop':
            await query.message.reply_text('С товарами в нашем магазине вы можете ознакомится по этой ссылке')
        case'feedback':
            await query.message.reply_text('Посмотреть отзывы вы можете здесь https://t.me/dsk_reviews')
        case 'calc':
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(text='Обувь', callback_data='product1'),
                ],
                [
                    InlineKeyboardButton(text='Одежда', callback_data='product3'),
                    InlineKeyboardButton(text='Аксессуары', callback_data='product4'),
                ]
            ])
            await query.message.reply_text('Выберите категорию:', reply_markup=reply_markup)
        case 'product1':
            await query.message.reply_text('Сколько позиций в вашем заказе?')
