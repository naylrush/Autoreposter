import json

from InstagramBot import InstagramBot
from datetime import datetime, date, time


def main():
    # add argparse
    with open('app_data.hidden') as app_data_json:
        app_data = json.load(app_data_json)

    with open('access_code.hidden') as access_code_json:
        access_code = json.load(access_code_json)

    insta_bot = InstagramBot(app_data, access_code)

    # download today's posts
    today_dttm = datetime.combine(datetime.now().date(), time())
    insta_bot.download_user_posts(begin_dttm=today_dttm)


if __name__ == '__main__':
    main()
