import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (CallbackContext, CommandHandler, Filters,
                          MessageHandler, Updater)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Добрый день! Это SelfStorageBot",
        reply_markup=get_main_menu())


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text)


def get_main_menu():
    custom_keyboard = [['Заказать аренду', 'Мои заказы'], 
                    ['Правила хранения', 'Частые вопросы (FAQ)'],
                    ['Панель администратора']]
    return ReplyKeyboardMarkup(custom_keyboard)


def launch_bot(token):
    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    updater.start_polling()
    
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)



def get_bot_info(token):
    bot = telegram.Bot(token=token)
    print(bot.get_me())
