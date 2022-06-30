from environs import Env

from bot.bot import launch_bot


def main():
    env = Env()
    env.read_env()
    bot_token = env('BOT_TOKEN')
    launch_bot(bot_token)


if __name__ == '__main__':
    main()
