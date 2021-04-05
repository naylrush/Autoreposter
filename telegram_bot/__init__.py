import telebot
from telebot.types import BotCommand, Message

from hidden.tg.bot_token import bot_token
from instagram_bot import insta_bot
from telegram_bot.TelegramBot import TelegramBot

tg = telebot.TeleBot(bot_token)
tg_bot = TelegramBot(tg, insta_bot)

tg.set_my_commands([
    BotCommand('/set', 'Set @channel_username to post in it'),
    BotCommand('/take', 'Take Nth or 1st instagram post'),
    BotCommand('/update', 'Up to date instagram posts')
])


# handlers
@tg.message_handler(commands=['set'])
def set_channel(message: Message):
    print('"Set Channel" handler')
    tg_bot.set_channel(message)


@tg.message_handler(commands=['take'])
def take_post(message: Message):
    print('"Take Post" handler')
    tg_bot.take_post(message)


@tg.message_handler(commands=['update'])
def update_channel(message: Message):
    print('"Update Channel" handler')
    tg_bot.update_channel(message)


@tg.message_handler()
def try_again(message: Message):
    tg.reply_to(message, text='Try again')
