# self-storage-bot
Telegram bot for "SelfStorage" service


### How to install

Python3 should be already installed.

Download the [ZIP archive](https://github.com/Katsutami7moto/self-storage-bot/archive/refs/heads/main.zip) of the code and unzip it.
Then open terminal form unzipped directory and use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```commandline
pip install -r requirements.txt
```
Before you run any of the scripts, you may need to configure environmental variables:

1. Go to the unzipped directory and create a file with the name `.env` (yes, it has only the extension).
It is the file to contain environmental variables that usually store data unique to each user, thus you will need to create your own.
2. Copy and paste this to `.env` file:
```dotenv
BOT_TOKEN={telegram_bot_token}
LIST_OF_ADMINS='{user_id_1,user_id_2}'
```
3. Replace `{telegram_token}` with API token for the Telegram bot you have created with the help of [BotFather](https://telegram.me/BotFather). This token will look something like this: `958423683:AAEAtJ5Lde5YYfkjergber`.
4. Replace `{user_id_1,user_id_2}` with Telegram user ids with admin privilegies.

### How to use

```commandline
python3 main.py
```


### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).