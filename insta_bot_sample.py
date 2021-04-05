from datetime import datetime

from pytz import timezone

from InstagramBot import insta_bot


def main():
    # download today's posts
    today_dttm = datetime.now(tz=timezone('Europe/Moscow')).replace(hour=0, minute=0, second=0, microsecond=0)
    insta_bot.download_user_posts(begin_dttm=today_dttm)


if __name__ == '__main__':
    main()
