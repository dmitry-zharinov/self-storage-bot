import datetime
from functools import wraps

from environs import Env
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from .bot_helpers import read_json

env = Env()
env.read_env()

LIST_OF_ADMINS = list(map(int, env.list('LIST_OF_ADMINS')))
ORDERS_FILENAME = 'orders.json'


def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    custom_keyboard = [
        ['Заказать аренду', 'Мои заказы'],
        ['Правила хранения', 'Частые вопросы (FAQ)'],
    ]
    if is_user_admin(user_id):
        custom_keyboard.append(['Панель администратора'])

    return ReplyKeyboardMarkup(custom_keyboard)


def restricted(func):
    """Запрет доступа к обработчику для не-администраторов"""
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if not is_user_admin(user_id):
            print(f'Нет прав доступа для user_id {user_id}.')
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text='У вас нет прав доступа к данной опции меню!',
                reply_markup=get_main_menu(update.effective_user.id))
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def is_user_admin(user_id: int) -> bool:
    """Проверка: пользователь является администратором?"""
    if user_id in LIST_OF_ADMINS:
        return True
    return False


@restricted
def open_admin_panel(update: Update, context: CallbackContext):
    """Открыть панель администратора"""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Панель администратора',
        reply_markup=get_admin_keyboard())


@restricted
def show_overdue_orders(update: Update, context: CallbackContext):
    """Показать просроченные заказы"""
    overdue_orders = []
    orders: dict = read_json(ORDERS_FILENAME)
    current_date = datetime.datetime.today().date()
    for order, info in orders.items():
        end_time = info.get('end_time')

        if end_time:
            if datetime.datetime.fromisoformat(end_time).date() < current_date:
                user_id = info.get('user_id')
                overdue_orders.append(
                    f'<b>Заказ {order}</b>\n'
                    f'Клиент {info.get("user_name")}\n'
                    f'Telegram ID: <a href="tg://user?id={user_id}">{user_id}</a>\n'
                    f'Номер телефона: {info.get("feedback")}\n'
                    f'Заказ истёк: {info.get("end_time")}')
    if not overdue_orders:
        overdue_orders_msg = 'Нет просроченных заказов'
    else:
        overdue_orders_msg = '\n'.join(overdue_orders)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=overdue_orders_msg,
        parse_mode=ParseMode.HTML,
        reply_markup=get_admin_keyboard())


@restricted
def show_commercial_orders(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Людей сделало заказов с рекламы:',
        reply_markup=get_admin_keyboard())


@restricted
def show_current_orders(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Активные заказы на доставку:',
        reply_markup=get_admin_keyboard())


def get_admin_keyboard():
    custom_keyboard = [
        ['Текущие заказы'], ['Просроченные заказы'],
        ['Эффективность рекламы'], ['Главное меню']
    ]
    return ReplyKeyboardMarkup(custom_keyboard)
