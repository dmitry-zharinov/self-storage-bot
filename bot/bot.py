import logging

from telegram import Bot, ReplyKeyboardMarkup, Update, ParseMode
from telegram.ext import (CallbackContext, CommandHandler, Dispatcher, Filters,
                          MessageHandler, Updater)

from .bot_helpers import is_user_admin, restricted, read_json


def get_main_menu(user_id) -> ReplyKeyboardMarkup:
    custom_keyboard = [
        ['Заказать аренду', 'Мои заказы'],
        ['Правила хранения', 'Частые вопросы (FAQ)'],
    ]
    if is_user_admin(user_id):
        custom_keyboard.append(['Панель администратора'])

    return ReplyKeyboardMarkup(custom_keyboard)


def get_hello_message() -> str:
    # TODO: грузить текст приветственного сообщения из JSON
    pass


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        # text=get_hello_message()
        text='Добрый день! Это SelfStorageBot',
        reply_markup=get_main_menu(user_id)
    )


def return_to_main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Главное меню',
        reply_markup=get_main_menu(user_id)
    )


def get_rental_terms_text() -> str:
    # TODO: грузить текст условий заказа аренды из JSON
    pass


def order_rental(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Сделать заказ'], ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        # text=get_rental_terms_text(),
        text="""Закажите аренду на нашем складе по адресу: ...
Доставка до склада бесплатна.""",
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def make_order(update: Update, context: CallbackContext):
    pass


def get_active_orders() -> list:
    # TODO: грузить список названий текущих заказов из JSON
    pass


def get_unpaid_orders() -> list:
    # TODO: грузить список названий неоплаченных заказов из JSON
    pass


def get_complete_orders() -> list:
    # TODO: грузить список названий завершённых заказов из JSON
    pass


def show_user_orders(update: Update, context: CallbackContext):
    unpaid_orders = get_unpaid_orders()
    active_orders = get_active_orders()
    complete_orders = get_complete_orders()

    if not (active_orders or unpaid_orders or complete_orders):
        msg = 'Вы ещё не делали заказов.'
    else:
        msg = f"""У вас:
{f'- {len(unpaid_orders)} неоплаченных заказов;' if unpaid_orders else None}
{f'- {len(active_orders)} активных заказов;' if active_orders else None}
{f'- {len(complete_orders)} завершённых заказов;' if complete_orders else None}
"""
    custom_keyboard = []
    if unpaid_orders:
        custom_keyboard.append(['Неоплаченные заказы'])
    if active_orders:
        custom_keyboard.append(active_orders)
    if complete_orders:
        custom_keyboard.append(['Завершённые заказы'])
    custom_keyboard.append(['Главное меню'])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def show_unpaid_orders():
    pass


def show_complete_orders():
    pass


def get_rules_text() -> str:
    # TODO: грузить текст правил хранения из JSON
    pass


def show_rules(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        # text=get_rules_text(),
        text='Правила',
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def get_faq_text() -> str:
    faq = read_json('faq.json')
    faq_text = '\n'.join(f'<b>{question}</b>\n{answer}\n'
                         for question, answer in faq.items())
    return faq_text


def show_faq(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Главное меню']
    ]

    faq_text = get_faq_text()
    msg_len = len(faq_text)
    if msg_len > 4096:
        for x in range(0, msg_len, 4096):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=faq_text[x:x+4096],
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardMarkup(custom_keyboard)
            )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=faq_text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(custom_keyboard)
        )


@restricted
def open_admin_panel(update: Update, context: CallbackContext):
    # current_orders = admin_current_orders()
    # overdue_orders = admin_overdue_orders()
    # commercial_orders = get_commercial_orders()

    custom_keyboard = [
        ['Текущие заказы'], ['Просроченные заказы'],
        ['Эффективность рекламы'], ['Главное меню']
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Панель администратора',
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def show_order_status(order_name: str,
                      update: Update, context: CallbackContext):
    pass


def handle_menu_actions(update: Update, context: CallbackContext):
    action_text = update.message.text
    if action_text.startswith('#'):
        show_order_status(action_text, update, context)
    else:
        menu_actions = {
            'Главное меню': return_to_main_menu,
            'Заказать аренду': order_rental,
            'Сделать заказ': make_order,
            'Мои заказы': show_user_orders,
            'Неоплаченные заказы': show_unpaid_orders,
            'Завершённые заказы': show_complete_orders,
            'Правила хранения': show_rules,
            'Частые вопросы (FAQ)': show_faq,
            'Панель администратора': open_admin_panel
        }
        action = menu_actions[action_text]
        action(update, context)


def launch_bot(token):
    updater = Updater(token=token, use_context=True)
    dispatcher: Dispatcher = updater.dispatcher

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()

    menu_actions_handler = MessageHandler(Filters.text, handle_menu_actions)
    dispatcher.add_handler(menu_actions_handler)


def get_bot_info(token):
    bot = Bot(token=token)
    print(bot.get_me())
