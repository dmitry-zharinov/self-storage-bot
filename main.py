import os

from dotenv import load_dotenv

from bot.bot import launch_bot


def main():
    load_dotenv()
    bot_token = os.environ['BOT_TOKEN']
    launch_bot(bot_token)


if __name__ == '__main__':
    main()
