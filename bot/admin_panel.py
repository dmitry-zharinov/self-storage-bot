from collections import Counter
from datetime import datetime
from functools import wraps
from pathlib import Path

import pandas
from environs import Env
from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext

from .bot_helpers import get_doc, get_location, read_json
from .constants import DATA_FOLDER, ORDERS_FILENAME, STATUS_UNPAID

env = Env()
env.read_env()

LIST_OF_ADMINS = list(map(int, env.list('LIST_OF_ADMINS')))


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


def get_overdue_orders():
    """Найти просроченные заказы"""
    overdue_orders = dict()
    orders: dict = read_json(ORDERS_FILENAME)
    current_date = datetime.today().date()
    for order, info in orders.items():
        end_time = info.get('end_time')
        if end_time:
            if datetime.fromisoformat(end_time).date() < current_date:
                overdue_orders[order] = info
    return overdue_orders


@restricted
def show_overdue_orders(update: Update, context: CallbackContext):
    """Показать просроченные заказы"""
    overdue_orders_text = []
    overdue_orders = get_overdue_orders()
    for order, info in overdue_orders.items():
        user_id = info.get('user_id')
        telegram_id = f'<a href="tg://user?id={user_id}">{user_id}</a>'
        overdue_orders_text.append(
            f'<b>Заказ {order}</b>\n'
            f'Клиент {info.get("user_name")}\n'
            f'Telegram ID: {telegram_id}\n'
            f'Номер телефона: {info.get("feedback")}\n'
            f'Заказ истёк: {info.get("end_time")}\n')
    if not overdue_orders_text:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нет просроченных заказов',
            parse_mode=ParseMode.HTML,
            reply_markup=get_admin_keyboard())
    else:
        for order in overdue_orders_text:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=order,
                parse_mode=ParseMode.HTML,
                reply_markup=get_admin_keyboard())


@restricted
def show_commercial_orders(update: Update, context: CallbackContext):
    orders: dict = read_json(ORDERS_FILENAME)
    order_dates = list()
    for order, info in orders.items():
        start_date = info.get('start_time')
        if start_date:
            order_dates.append(start_date)
    plot_filename = create_orders_diagram(order_dates)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'Всего заказов через бота: {len(order_dates)}',
    )
    context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=get_doc(plot_filename),
        reply_markup=get_admin_keyboard())


def create_orders_diagram(order_dates: list):
    """Создать диаграмму с распредлением заказов по месяцам"""
    plot_filename = 'plot.png'
    orders_counter = Counter(order_dates)
    orders_df = pandas.DataFrame(
        {
            'date': orders_counter.keys(),
            'counts': orders_counter.values()
        }
    )
    orders_df['date'] = pandas.to_datetime(orders_df['date'])
    result_df = orders_df.groupby(orders_df['date'].dt.to_period('M')).sum()
    result_df = result_df.resample('M').asfreq().fillna(0)
    result_plot = result_df.plot(kind='bar')
    figure = result_plot.get_figure()
    figure.savefig(
        Path.cwd() / Path(DATA_FOLDER) / plot_filename,
        bbox_inches='tight')
    return plot_filename


@restricted
def show_current_orders(update: Update, context: CallbackContext):
    """Активные заказы на доставку"""
    orders: dict = read_json(ORDERS_FILENAME)
    order_text = ''
    for order, info in orders.items():
        status = info.get('status')

        if status is STATUS_UNPAID:
            user_id = info.get('user_id')
            telegram_id = f'<a href="tg://user?id={user_id}">{user_id}</a>'
            client_address = info.get("client_address")

            if client_address:
                order_text = f'<b>Заказ {order}</b>\n' \
                             f'Клиент {info.get("user_name")}\n' \
                             f'Telegram ID: {telegram_id}\n' \
                             f'Номер телефона: {info.get("feedback")}\n' \
                             f'Адрес: {client_address}\n'
                msg = context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=order_text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=get_admin_keyboard())

                location = get_location(client_address)
                context.bot.sendLocation(
                    chat_id=update.effective_chat.id,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    reply_to_message_id=msg.message_id)

    if not order_text:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Нет активных заказов на доставку',
            reply_markup=get_admin_keyboard())


def get_admin_keyboard():
    """Меню для панели администратора"""
    custom_keyboard = [
        ['Текущие заказы'], ['Просроченные заказы'],
        ['Эффективность рекламы'], ['Главное меню']
    ]
    return ReplyKeyboardMarkup(custom_keyboard)
