import logging
from datetime import datetime

from telegram import ParseMode, ReplyKeyboardMarkup, Update
from telegram.ext import (CallbackContext, CommandHandler, Dispatcher, Filters,
                          MessageHandler, Updater)

from .admin_panel import (is_user_admin, open_admin_panel,
                          show_commercial_orders, show_current_orders,
                          show_overdue_orders)
from .bot_helpers import generate_qrcode, get_doc, read_json, write_json
from .constants import (ORDERS_FILENAME, STATUS_ACTIVE, STATUS_COMPLETE,
                        STATUS_UNPAID)

filling_orders: dict = {}  # ключ - user_id, значение - словарь заказа

created_orders = []  # значение - словарь заказа


# Как выглядит словарь каждого заказа:
# {
#     'user_id': '',
#     'order_id': '',
#     'user_name': '',
#     'status': '',
#     'name': '',
#     'phone_number': '',
#     'client_address': '',
#     'stotage_size': '',
#     'storage_time': '',
#     'start_time': '',
#     'end_time': '',
#     'need_delivery': '',
# }


def fill_in_field(update: Update, field: str, value):
    filling_orders[update.effective_user.id][field] = value


def get_processed_order(order_name: str) -> dict:
    processed_orders: dict = read_json(ORDERS_FILENAME)
    return processed_orders[order_name]


def get_user_orders(user_id: int) -> dict:
    orders: dict = read_json(ORDERS_FILENAME)
    user_orders = {order: info for order, info in orders.items()
                   if info.get('user_id') == user_id}
    return user_orders


def store_created_orders(orders: list, user_id: int):
    current_order_id = 1
    processed_orders: dict = read_json(ORDERS_FILENAME)
    if processed_orders:
        current_order_id = max(map(lambda x: int(x.strip('#')),
                                   processed_orders.keys())) + 1
    for order in orders:
        order['order_id'] = current_order_id
        order['user_id'] = user_id
        order['status'] = STATUS_UNPAID
        order['start_time'] = str(datetime.today().date())
        processed_orders[f'#{current_order_id}'] = order
        current_order_id += 1
    write_json(processed_orders, ORDERS_FILENAME)


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


def get_rental_terms_text() -> list:
    terms = read_json('rental_terms.json')
    terms_text = []
    for section, text in terms.items():
        text_ = '\n\n'.join(text)
        terms_text.append(f'<b>{section}</b>\n\n{text_}')
    return terms_text


def order_rental(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Сделать заказ'], ['Главное меню']
    ]
    terms_text = get_rental_terms_text()
    for section in terms_text:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=section,
            parse_mode=ParseMode.HTML,
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
        text='Пожалуйста, выберите примерный объём вещей. '
             'Вам не нужно замерять их, все необходимые замеры '
             'будут сделаны либо мувером, либо при приёме на склад.',
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


def ask_for_personal_data(update: Update, context: CallbackContext):
    # TODO: запросить ФИО закзачика, номер телефона и адрес забора вещей
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
    filename = 'personal_data_terms.pdf'
    context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=get_doc(filename),
        filename=filename,
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
        store_created_orders(created_orders, user_id)
        created_orders.clear()
    msg = 'Благодарим Вас за оставленную заявку!'
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        reply_markup=get_main_menu(user_id)
    )


def get_orders_by_status(orders: dict, status: int) -> list:
    result_orders = []
    for order, info in orders.items():
        if info.get('status') == status:
            result_orders.append(
                f'<b>Заказ {order}</b> от {info.get("start_time")}\n'
                f'Размер хранения: {info.get("storage_size")}\n'
                f'Сроки хранения: {info.get("storage_time")}\n')
    return result_orders


def show_user_orders(update: Update, context: CallbackContext):
    user_orders = get_user_orders(update.effective_user.id)

    unpaid_orders = get_orders_by_status(user_orders, STATUS_UNPAID)
    active_orders = get_orders_by_status(user_orders, STATUS_ACTIVE)
    complete_orders = get_orders_by_status(user_orders, STATUS_COMPLETE)

    if not (unpaid_orders or active_orders or complete_orders):
        msg = 'Вы ещё не делали заказов.'
    else:
        unpaid_orders_len = len(unpaid_orders) if unpaid_orders else 'Нет'
        active_orders_len = len(active_orders) if active_orders else 'Нет'
        complete_order_len = len(complete_orders) if complete_orders else 'Нет'

        msg = f"""У вас:
    {f'- {unpaid_orders_len} неоплаченных заказов;'}
    {f'- {active_orders_len} активных заказов;'}
    {f'- {complete_order_len} завершённых заказов;'}
"""
    custom_keyboard = []
    if unpaid_orders:
        custom_keyboard.append(['Неоплаченные заказы'])
    if active_orders:
        custom_keyboard.append(['Активные заказы'])
    if complete_orders:
        custom_keyboard.append(['Завершённые заказы'])
    custom_keyboard.append(['Главное меню'])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(custom_keyboard)
    )


def show_unpaid_orders(update: Update, context: CallbackContext):
    user_orders = get_user_orders(update.effective_user.id)
    unpaid_orders = get_orders_by_status(user_orders, STATUS_UNPAID)

    custom_keyboard = [
        ['Мои заказы'], ['Главное меню']
    ]
    for order in unpaid_orders:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{order}',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(custom_keyboard)
        )


def show_active_orders(update: Update, context: CallbackContext):
    user_orders = get_user_orders(update.effective_user.id)
    active_orders = get_orders_by_status(user_orders, STATUS_ACTIVE)

    custom_keyboard = [
        ['Мой QR-код'], ['Мои заказы'], ['Главное меню']
    ]
    for order in active_orders:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{order}',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(custom_keyboard)
        )


def show_qr_code(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Мои заказы'], ['Главное меню']
    ]
    user_id = update.effective_user.id
    user_orders = get_user_orders(user_id)
    active_orders = get_orders_by_status(user_orders, STATUS_ACTIVE)

    if active_orders:
        storage_data = str(update.effective_chat.id)
        qr_filename = generate_qrcode(storage_data)

        context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=get_doc(qr_filename),
            filename=qr_filename,
            caption='QR-код для доступа на склад.\n'
                    'При необходимости Вы сможете вернуть вещи '
                    '(или часть вещей) в бокс до истечения срока аренды.',
            reply_markup=ReplyKeyboardMarkup(custom_keyboard))
    else:
        context.bot.send_message(
            chat_id=user_id,
            text='У вас нет активных заказов!',
            reply_markup=get_main_menu(user_id))


def show_complete_orders(update: Update, context: CallbackContext):
    user_orders = get_user_orders(update.effective_user.id)
    complete_orders = get_orders_by_status(user_orders, STATUS_COMPLETE)

    custom_keyboard = [
        ['Мои заказы'], ['Главное меню']
    ]
    for order in complete_orders:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'{order}',
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(custom_keyboard)
        )


def get_rules_text() -> str:
    rules: list = read_json('rules.json')
    rules_text = '\n'.join(rules)
    return rules_text


def show_rules(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=get_rules_text(),
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
        '1 месяц': ask_for_personal_data,
        '3 месяца': ask_for_personal_data,
        'Полгода': ask_for_personal_data,
        'Год и более': ask_for_personal_data,
        'Выбрать время позже': ask_for_personal_data,
        ###
        'Обработка персональных данных': show_personal_data_terms,
        'Подать заявку': send_order,
        ###
        'Мои заказы': show_user_orders,
        'Неоплаченные заказы': show_unpaid_orders,
        'Активные заказы': show_active_orders,
        'Завершённые заказы': show_complete_orders,
        'Мой QR-код': show_qr_code,
        ###
        'Правила хранения': show_rules,
        'Частые вопросы (FAQ)': show_faq,
        ###
        'Панель администратора': open_admin_panel,
        'Просроченные заказы': show_overdue_orders,
        'Текущие заказы': show_current_orders,
        'Эффективность рекламы': show_commercial_orders,
    }
    action_text = update.message.text
    if action_text.startswith('+'):
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
