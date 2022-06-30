import os

import django
from dotenv import load_dotenv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'self_storage.settings')
django.setup()

from bot.bot import launch_bot


def main():
    
    load_dotenv()
    bot_token = os.environ['BOT_TOKEN']
    launch_bot(bot_token)


if __name__ == '__main__':
    main()
