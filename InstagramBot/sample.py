from hidden.access_code import access_code
from hidden.app_data import app_data

from datetime import datetime, time
from InstagramBot import InstagramBot


def main():
    insta_bot = InstagramBot(app_data, access_code)

    # download today's posts
    today_dttm = datetime.combine(datetime.now().date(), time())
    insta_bot.download_user_posts(begin_dttm=today_dttm)


if __name__ == '__main__':
    main()
