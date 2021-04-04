import json

from InstagramBot import InstagramBot


def main():
    # add argparse
    with open('app_data.hidden') as app_data_json:
        app_data = json.load(app_data_json)

    with open('access_code.hidden') as access_code_json:
        access_code = json.load(access_code_json)

    insta_bot = InstagramBot(app_data, access_code)

    insta_bot.download_all_user_posts()


if __name__ == '__main__':
    main()
