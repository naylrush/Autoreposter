from datetime import datetime, time

from InstagramBot import insta_bot


def main():
    # download today's posts
    today_dttm = datetime.combine(datetime.now().date(), time())
    insta_bot.download_user_posts(begin_dttm=today_dttm)


if __name__ == '__main__':
    main()
