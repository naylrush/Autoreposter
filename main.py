from threading import Thread
from time import sleep

from telegram_bot import tg_bot


def update_channel_every(interval_s: int):
    while True:
        tg_bot.update_channel()
        sleep(interval_s)


if __name__ == '__main__':
    # Update channel every minute
    updater = Thread(target=update_channel_every, args=(60,))
    updater.daemon = True  # will be stopped after main thread death
    updater.start()

    tg_bot.polling(none_stop=True)
