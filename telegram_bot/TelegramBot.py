import json
import re
from time import sleep
from typing import List

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Message, InputMediaPhoto, InputMediaVideo
from telegram.constants import MAX_CAPTION_LENGTH

import hidden.tg.channel_dict
from hidden.tg.admins import admins
from hidden.tg.channel_dict import channel_dict
from instagram_bot.InstagramBot import InstagramBot
from instagram_bot.MediaType import MediaType
from instagram_bot.SimplePost import SimplePost
from telegram_bot.Channel import Channel


class TelegramBot:
    def __init__(self, tg: TeleBot, insta_bot: InstagramBot, debug: bool = True):
        self.tg = tg
        self.insta_bot = insta_bot
        self.channel = Channel(**channel_dict)

        self.debug = debug

    def polling(self, none_stop=False):
        self.tg.polling(none_stop=none_stop)

    def answer(self, message: Message, text):
        if message:
            self.tg.send_message(message.chat.id, text=text)
        if self.debug:
            print(text)

    def check_admin(self, message):
        if message.chat.username not in admins:
            self.answer(message, 'You are not an admin')
            return False
        return True

    def check_channel_set(self, message):
        if not self.channel:
            self.answer(message, 'Channel is not set')
            return False
        return True

    def save_channel(self):
        """
        Saves channel into 'hidden.tg.channel' which can be imported and used as variable
        """
        try:
            with open(hidden.tg.channel_dict.__file__, 'w') as out:
                channel_dict_py = f'import datetime\n\nchannel_dict = {self.channel.__dict__}\n'
                out.write(channel_dict_py)
        except FileNotFoundError as e:
            print(f'{e.strerror}: "{e.filename}"')

    def set_channel(self, message: Message):
        """
        If user is admin, trys to get channel_username and saves new channel, if successfull

        :param message:
        """
        if self.check_admin(message):
            match = re.match('/set (@\\w{5,64})', message.text)
            if not match:
                self.answer(message, 'Write a channel using @channel')
                return

            channel_username = match.group(1)
            try:
                channel_id = self.tg.get_chat(chat_id=channel_username).id
                self.channel = Channel(channel_id)
                self.save_channel()

                self.answer(message, 'Bot was connected')
            except ApiException as e:
                self.answer(message, get_tg_api_exception_text(e))

    def take_post(self, message: Message):
        """
        If user is admin, sends Nth post to the saved channel

        :param message:
        """
        if self.check_admin(message) and self.check_channel_set(message):
            self.answer(message, 'Taking...')
            match = re.match('/take (-?[0-9]+)', message.text)
            n = int(match.group(1)) if match else 1

            if n <= 0:
                self.answer(message, 'The number must be 1 or greater')
                return

            posts = self.insta_bot.get_user_posts()

            if n > len(posts):
                self.answer(message, f'Too big number. Current post count is {len(posts)}')
                return

            post = posts[n - 1]
            try:
                self.send_posts([post])
                self.answer(message, f'#{n} post was sent')
            except ApiException as e:
                self.answer(message, get_tg_api_exception_text(e))

    def update_channel(self, message: Message = None):
        """
        Up to date instagram posts

        :param message:
        """
        if not message or self.check_admin(message) and self.check_channel_set(message):
            self.answer(message, 'Updating...')
            # get posts newer then last updated dttm of channel
            posts = self.insta_bot.get_user_posts(begin_dttm=self.channel.update())
            if not posts:
                self.answer(message, 'Is up to date')
                return

            # reverse posts to send them in order of novelty
            posts.reverse()
            try:
                self.send_posts(posts)
                self.answer(message, f'{len(posts)} posts were sent')
            except ApiException as e:
                self.answer(message, get_tg_api_exception_text(e))
            # save the channel last updated dttm
            self.save_channel()

    def send_posts(self, posts: List[SimplePost]):
        """
        Sends given posts and sleeps 6 second after sending every post because of limit of 20 messages per minute

        :param posts:
        """
        size = len(posts)
        for i, post in enumerate(posts, 1):
            # to send not greater than 20 messages to the channel
            data = convert_post_to_input_data(post)
            chat_id = self.channel.id

            if not post.caption or len(post.caption) <= MAX_CAPTION_LENGTH:
                data[0].caption = post.caption
                self.tg.send_media_group(chat_id=chat_id, media=data)
                print(f'Content was sent [{i}/{size}]')
            else:
                self.tg.send_media_group(chat_id=chat_id, media=data)
                self.tg.send_message(chat_id=chat_id, text=post.caption)
            sleep(6)


def get_tg_api_exception_text(e):
    return json.loads(e.result.text).get('description')


def create_input_data(media, media_type: MediaType):
    if media_type == MediaType.IMAGE:
        return InputMediaPhoto(media=media)
    elif media_type == MediaType.VIDEO:
        return InputMediaVideo(media=media)


def convert_post_to_input_data(post):
    content = post.urlopen_content()
    return [create_input_data(media, media_type) for (media, media_type) in content]
