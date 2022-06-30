import logging

from telegram import Update, ReplyKeyboardMarkup, Bot, KeyboardButton
from telegram.ext import (CallbackContext, CommandHandler, Dispatcher,
                          Filters, MessageHandler, Updater)


def get_main_menu():
    custom_keyboard = [
        ['Заказать аренду', 'Мои заказы'],
        ['Правила хранения', 'Частые вопросы (FAQ)'],
        ['Панель администратора']
    ]
    return ReplyKeyboardMarkup(custom_keyboard)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Добрый день! Это SelfStorageBot',
        reply_markup=get_main_menu()
    )


def return_to_main_menu(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text='Главное меню',
        reply_markup=get_main_menu()
    )


def order_rental(update: Update, context: CallbackContext):
    custom_keyboard = [
        ['Сделать заказ'], ['Главное меню']
    ]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""Закажите аренду на нашем складе по адресу: ...
Доставка до склада бесплатна""",
        reply_markup=ReplyKeyboardMarkup(custom_keyboard,
                                         one_time_keyboard=True)
    )


def handle_menu_actions(update: Update, context: CallbackContext):
    menu_actions = {
        'Главное меню': return_to_main_menu,
        'Заказать аренду': order_rental,
        'Сделать заказ': '',
        'Мои заказы': '',
        'Правила хранения': '',
        'Частые вопросы (FAQ)': '',
        'Панель администратора': '',
    }
    action = menu_actions[update.message.text]
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
