from datetime import datetime

from dateutil.relativedelta import relativedelta
from telegram import ParseMode
from telegram.ext import CallbackContext

from .admin_panel import get_overdue_orders
from .bot_helpers import read_json
from .constants import ORDERS_FILENAME, STATUS_ACTIVE


def order_expired(context: CallbackContext):
    '''Cрок аренды истёк'''
    overdue_orders = get_overdue_orders()
    for order, info in overdue_orders.items():
        user_id = info.get('user_id')
        expired = datetime.fromisoformat(
            info.get('end_time')).date()+relativedelta(months=6)
        context.bot.send_message(
            chat_id=user_id,
            parse_mode=ParseMode.HTML,
            text=f'<b>Уведомление об окончании аренды</b>\n\n'
            f'Уважаемый {info.get("user_name")}!\n'
            f'Срок хранения вашего заказа {order} '
            f'истёк {info.get("end_time")}.\n'
            f'Вещи будут храниться 6 месяцев по повышенному тарифу (+ 40%).\n'
            f'Просим забрать заказ до {expired} '
        )


def order_expires_soon(context: CallbackContext):
    '''Подходит конец срока аренды'''
    notification_time = [30, 14, 7, 3]
    orders: dict = read_json(ORDERS_FILENAME)
    for order, info in orders.items():
        status = info.get('status')
        if status is STATUS_ACTIVE:
            user_id = info.get('user_id')
            current_date = datetime.today().date()
            end_time = info.get('end_time')
            if end_time:
                end_date = datetime.fromisoformat(end_time).date()
                days_left = end_date - current_date
                print(f'дней осталось: {days_left}')
                if days_left.days in notification_time:
                    context.bot.send_message(
                        chat_id=user_id,
                        parse_mode=ParseMode.HTML,
                        text=f'<b>Уведомление о скором окончании аренды</b>\n\n'
                        f'Уважаемый {info.get("user_name")}!\n'
                        f'Через {days_left.days} дня истечёт '
                        f'срок хранения вашего заказа {order}.\n'
                        f'Просим продлить аренду или забрать вещи до {end_date}'
                    )
