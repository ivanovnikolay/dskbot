import logging
from os import getenv
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    error,
    ChatMember,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
    ExtBot,
)
from .yuan import yuan_exchange_rate


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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
            CallbackQueryHandler(apps, pattern='apps'),
            CallbackQueryHandler(user_subscribed, pattern='user_subscribed'),
        ],
        states={
            CALCULATE_START: [CallbackQueryHandler(calculate_start)],
            CALCULATE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_count)],
            CALCULATE_TOTAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_total)],
        },
        fallbacks=[CommandHandler(('start', 'cancel'), start)],
    ))

    return app


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await _is_user_subscribed(context.bot, update.effective_user.id):
        text = f'Привет! Я бот пчёлка 🐝\n\nТекущий курс рубля к юаню: 1¥ = {yuan_exchange_rate()}₽'
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(text='🛍 Магазин', url='https://docs.google.com/spreadsheets/d/11r7_7HVRW-cU_t93-BB68Qsn2GbQQEfvwkkVkZQsfuE/edit#gid=0'),
                InlineKeyboardButton(text='📊 Отзывы', url='https://t.me/dsk_reviews/1'),
            ],
            [
                InlineKeyboardButton(text='🔥 Сделать заказ', callback_data='order'),
            ],
            [
                InlineKeyboardButton(text='🛒 Приложения для выборов товара', callback_data='apps'),
            ],
            [
                InlineKeyboardButton(text='🧮 Рассчитать стоимость доставки', callback_data='calculate'),
            ],
        ])
    else:
        text = f'Привет! Этот бот является частью канала {channel_name} поэтому для работы с ботом, пожалуйста, подпишитесь на наш канал'
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text='📣 Подписаться на канал', url=f'https://t.me/{channel_name}')],
            [InlineKeyboardButton(text='✅ Я подписался', callback_data='user_subscribed')],
        ])
    await (update.message or update.callback_query.message).reply_text(text, reply_markup=reply_markup)
    return ConversationHandler.END


async def order(update: Update, _):
    await update.callback_query.message.reply_text('Чтобы сделать заказ напишите @dsk_support')


async def apps(update: Update, _):
    await update.callback_query.message.reply_text('Приложения для выборов товара:', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='Poizon (iOS)', url='https://apps.apple.com/app/id1012871328')],
        [InlineKeyboardButton(text='Poizon (Android)', url='https://play.google.com/store/apps/details?id=com.shizhuang.poizon.hk&hl=ru&gl=US&cc_key=')],
        [InlineKeyboardButton(text='95 (iOS)', url='https://apps.apple.com/app/id1488709429')],
    ]))


async def calculate(update: Update, _):
    await update.callback_query.message.reply_text('Выберите категорию:', reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton(text='👟 Обувь', callback_data='1400')],
        [InlineKeyboardButton(text='👕 Одежда', callback_data='600')],
        [InlineKeyboardButton(text='🎒 Аксессуары', callback_data='700')],
    ]))
    return CALCULATE_START


async def calculate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['shipping'] = int(update.callback_query.data)
    await update.callback_query.message.reply_text('Введите количество товара:')
    return CALCULATE_COUNT


async def calculate_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(update.message.text)
    except Exception:
        await update.message.reply_text('Не удалось прочитать количество товара.\nПожалуйста, введите количество товара:')
        return CALCULATE_COUNT

    context.user_data['count'] = count
    await update.message.reply_text('Введите общую сумму заказа в юанях:')
    return CALCULATE_TOTAL


async def calculate_total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = round((float(update.message.text)+50) * yuan_exchange_rate(), 0)
    except Exception:
        await update.message.reply_text('Не удалось прочитать общую сумму заказа.\nПожалуйста, введите общую сумму заказа в юанях:')
        return CALCULATE_TOTAL

    shipping = context.user_data['shipping']*context.user_data['count']
    comission_total = context.user_data['count'] * comission
    text = f'Стоимость заказа: {amount}₽\n'
    text += f'Доставка: {shipping}₽\n'
    text += f'----------------------\n'
    text += f'<b>ИТОГО: {amount + shipping+comission_total}₽</b>\n\n'
    await update.message.reply_text(text, parse_mode='html')
    return await start(update, context)


async def user_subscribed(*args, **kwargs):
    return await start(*args, **kwargs)


async def _is_user_subscribed(bot: ExtBot, user_id):
    try:
        member = await bot.get_chat_member(channel_name, user_id)
        return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
    except error.TelegramError:
        log.exception('_is_user_subscribed failed')
        return False
