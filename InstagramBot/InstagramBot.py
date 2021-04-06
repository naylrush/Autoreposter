from collections import Counter
from typing import List

from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
from instagram_basic_display.InstagramBasicDisplayException import InstagramBasicDisplayException

import hidden.insta.access_token
from InstagramBot.MediaType import MediaType
from InstagramBot.SimplePost import SimplePost
from hidden.insta.access_token import access_token


class InstagramBot:
    def __init__(self, app_data: dict, access_code=None):
        self.insta = InstagramBasicDisplay(**app_data)

        self.access_token = self.refresh_or_retrieve_access_token(access_token, access_code)
        self.save_access_token()

        self.insta.set_access_token(self.access_token)

    def refresh_or_retrieve_access_token(self, saved_token: str, access_code: str) -> str:
        """
        If previously used access token is not None and is still not expired, function returns new access token
        Otherwise, function gets new access token using access code is provided

        :param saved_token: previously used access token
        :param access_code: access code has to be provided to get new access token
        :return: new access token
        """
        try:
            if saved_token:
                try:
                    return self.refresh_access_token(saved_token)
                except InstagramBasicDisplayException:
                    pass

            return self.retrieve_access_token(access_code)
        except InstagramBasicDisplayException:
            print(f'You need to update access code! Follow:\n{self.get_login_url()}')
            raise

    def get_login_url(self) -> str:
        """
        :return: login URL you need to follow
        """
        return self.insta.get_login_url()

    def retrieve_access_token(self, access_code: str) -> str:
        """
        Retrieves and saves access token based on access code

        :return: access token
        """
        # Get the short lived access token (valid for 1 hour)
        short_lived_token = self.insta.get_o_auth_token(access_code)

        # Exchange this token for a long lived token (valid for 60 days)
        long_lived_token = self.insta.get_long_lived_token(short_lived_token.get('access_token'))

        print('Access token was successfully retrieved')

        # Get new access token
        return long_lived_token.get('access_token')

    def refresh_access_token(self, token: str) -> str:
        """
        Retrieves and saves new access token based on previously got token

        :return: access token
        """
        # Exchange this token for a long lived token (valid for 60 days)
        long_lived_token = self.insta.refresh_token(token)

        print('Access token was successfully refreshed')

        # Get new access token
        return long_lived_token.get('access_token')

    def save_access_token(self):
        """
        Saves access token into 'hidden.insta.access_token' which can be imported and used as variable
        """
        try:
            with open(hidden.insta.access_token.__file__, 'w') as out:
                out.write(f"access_token = '{self.access_token}'\n")
        except FileNotFoundError as e:
            print(f'{e.strerror}: "{e.filename}"')

    def get_user_posts(self, begin_dttm=None) -> List[SimplePost]:
        """
        Requires access token
        Gets user posts after date and time if given or all user posts

        :param begin_dttm: begin datetime or None
        :return: list of SimplePost
        """

        posts = convert_to_simple_posts(self.insta.get_user_media().get('data'))

        return list(filter(lambda post: post.dttm >= begin_dttm, posts)) if begin_dttm else posts

    def download_user_posts(self, begin_dttm=None) -> List[str]:
        """
        Requires access token
        Downloads user posts after date and time if given or all user posts

        :param begin_dttm: begin datetime or None
        :return: paths to downloaded files
        """
        return download_posts(self.get_user_posts(begin_dttm))


def convert_to_simple_posts(posts: List[dict]) -> List[SimplePost]:
    return list(map(lambda post: SimplePost(post), posts))


def download_posts(posts: List[SimplePost]) -> List[str]:
    """
    Downloads content from given posts

    :return paths to downloaded files
    """
    content_counter = Counter()
    post_count = len(posts)
    paths = []

    for post in posts:
        new_paths, new_counter = post.download_content()

        paths += new_paths
        content_counter.update(new_counter)

    print(f'Downloaded {content_counter.get(MediaType.IMAGE)} images and {content_counter.get(MediaType.VIDEO)} videos '
          f'from {post_count} posts')

    return paths
