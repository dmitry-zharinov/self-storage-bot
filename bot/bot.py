import logging

from telegram import ReplyKeyboardMarkup, Update, ParseMode
from telegram.ext import (CallbackContext, CommandHandler, Dispatcher,
                          Filters, MessageHandler, Updater)

from .bot_helpers import (is_user_admin, restricted, read_json, write_json,
                          get_doc)

filling_orders: dict = {}  # ключ - user_id, значение - словарь заказа

created_orders = []  # значение - словарь заказа


# Как выглядит словарь каждого заказа:
# {
#     'user_id': '',
#     'order_id': '',
#     'user_name': '',
#     'status': '',
#     'name': '',
#     'stotage_size': '',
#     'storage_time': '',
#     'start_time': '',
#     'end_time': '',
#     'feedback': '',
#     'need_delivery': '',
#     'client_address': '',
# }


def fill_in_field(update: Update, field: str, value):
    filling_orders[update.effective_user.id][field] = value


def get_processed_order(order_name: str) -> dict:
    processed_orders: dict = read_json('orders.json')
    return processed_orders[order_name]


def store_created_orders(orders: list):
    current_order_id = 1
    processed_orders: dict = read_json('orders.json')
    if processed_orders:
        current_order_id = max(map(lambda x: int(x.strip('#')),
                                   processed_orders.keys())) + 1
    for order in orders:
        order['order_id'] = current_order_id
        processed_orders[f'#{current_order_id}'] = order
        current_order_id += 1
    write_json(processed_orders, 'orders.json')


def get_main_menu(user_id: int) -> ReplyKeyboardMarkup:
    custom_keyboard = [
        ['Заказать аренду', 'Мои заказы'],
        ['Правила хранения', 'Частые вопросы (FAQ)'],
    ]
    if is_user_admin(user_id):
        custom_keyboard.append(['Панель администратора'])

    return ReplyKeyboardMarkup(custom_keyboard)


def get_hello_message() -> str:
    hello_message = read_json('hello.json')['hello']
    return hello_message


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_hello_message(),
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_menu(update.effective_user.id)
    )


def return_to_main_menu(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Главное меню',
        reply_markup=get_main_menu(update.effective_user.id)
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


def choose_storage_size(update: Update, context: CallbackContext):
    filling_orders[update.effective_user.id] = dict()
    custom_keyboard = [
        ['Менее половины комнаты', 'Комната'],
        ['2-комнатная квартира', '3-комнатная квартира'],
        ['Выбрать размер позже', 'Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Пожалуйста, выберите примерный объём вещей',
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def choose_storage_time(update: Update, context: CallbackContext):
    msg = ''
    storage_size = update.message.text
    if storage_size == 'Выбрать размер позже':
        msg = 'Вы сможете уточнить объём вещей' \
              'при обсуждении заказа с менеджером.\n'
        fill_in_field(update, 'storage_size', 'Обсудите с менеджером позже')
    else:
        fill_in_field(update, 'storage_size', storage_size)
    custom_keyboard = [
        ['1 месяц', '3 месяца'],
        ['Полгода', 'Год и более'],
        ['Выбрать время позже', 'Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f'{msg}Пожалуйста, выберите примерный срок хранения',
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def ask_for_feedback(update: Update, context: CallbackContext):
    msg = ''
    storage_time = update.message.text
    if storage_time == 'Выбрать время позже':
        msg = 'Вы сможете уточнить сроки хранения'
        msg = f'{msg}при обсуждении заказа с менеджером\\.\n'
        fill_in_field(update, 'storage_time', 'Обсудите с менеджером позже')
    else:
        fill_in_field(update, 'storage_time', storage_time)
    custom_keyboard = [
        ['Обработка персональных данных'],
        ['Главное меню']
    ]
    msg = f"""{msg}Пожалуйста, введите номер телефона для связи \
\\(обязательно в формате `+71234567890` \\)\\.
Сообщая его нам, Вы соглашаетесь с нашим Положением по обработке Ваших \
персональных данных\\.
Вы можете ознакомиться с ним, нажав кнопку в меню \
\\(загрузится небольшой PDF\\-файл\\)\\."""
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardMarkup(
            custom_keyboard, one_time_keyboard=True
        )
    )


def show_personal_data_terms(update: Update, context: CallbackContext):
    # TODO: найти PDF с Положением по обработке персональных данных
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=get_doc('personal_data_terms.pdf'),
        caption='Положение по обработке персональных данных'
    )
    custom_keyboard = [
        ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""Пожалуйста, введите номер телефона для связи \
\\(обязательно в формате `+71234567890` \\)\\.""",
        parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def confirm_order(feedback: str, update: Update, context: CallbackContext):
    fill_in_field(update, 'feedback', feedback)
    current_order = filling_orders[update.effective_user.id]
    msg = f"""Пожалуйста, проверьте вашу заявку перед подачей:

Объём вещей: {current_order['storage_size']}
Время хранения: {current_order['storage_time']}
Телефон для связи: {current_order['feedback']}

Если всё верно, нажмите кнопку "Подать заявку".
Менеджер свяжется с Вами по указанному номеру с 9:00 до 21:00.
"""
    custom_keyboard = [
        ['Подать заявку'], ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def send_order(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    created_orders.append(filling_orders[user_id])
    del filling_orders[user_id]
    if not filling_orders:
        store_created_orders(created_orders)
        created_orders.clear()
    msg = 'Благодарим Вас за оставленную заявку!'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=get_main_menu(user_id)
    )


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

    if not (unpaid_orders or active_orders or complete_orders):
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
    limit = 4096
    faq_text = get_faq_text()
    msg_len = len(faq_text)
    if msg_len > limit:
        for x in range(0, msg_len, limit):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=faq_text[x:x + limit],
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
    showing_order = get_processed_order(order_name)


def handle_menu_actions(update: Update, context: CallbackContext):
    menu_actions = {
        'Главное меню': return_to_main_menu,
        ###
        'Заказать аренду': order_rental,
        'Сделать заказ': choose_storage_size,
        ###
        'Менее половины комнаты': choose_storage_time,
        'Комната': choose_storage_time,
        '2-комнатная квартира': choose_storage_time,
        '3-комнатная квартира': choose_storage_time,
        'Выбрать размер позже': choose_storage_time,
        ###
        '1 месяц': ask_for_feedback,
        '3 месяца': ask_for_feedback,
        'Полгода': ask_for_feedback,
        'Год и более': ask_for_feedback,
        'Выбрать время позже': ask_for_feedback,
        ###
        'Обработка персональных данных': show_personal_data_terms,
        'Подать заявку': send_order,
        ###
        'Мои заказы': show_user_orders,
        'Неоплаченные заказы': show_unpaid_orders,
        'Завершённые заказы': show_complete_orders,
        ###
        'Правила хранения': show_rules,
        'Частые вопросы (FAQ)': show_faq,
        ###
        'Панель администратора': open_admin_panel,
    }
    action_text = update.message.text
    if action_text.startswith('#'):
        show_order_status(action_text, update, context)
    elif action_text.startswith('+'):
        confirm_order(action_text, update, context)
    elif action_text in menu_actions:
        action = menu_actions[action_text]
        action(update, context)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Пожалуйста, выберите действие из меню'
        )


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
