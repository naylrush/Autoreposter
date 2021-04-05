from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
from instagram_basic_display.InstagramBasicDisplayException import InstagramBasicDisplayException
from datetime import datetime
import urllib.request

from hidden.access_token import access_token


def download_jpg_by_url(url, filename):
    with urllib.request.urlopen(url) as photo_raw:
        with open(f'downloads/{filename}.jpg', 'wb') as photo_file:
            photo_file.write(photo_raw.read())


iso_time_format = '%Y-%m-%dT%H:%M:%S%z'


def get_post_dttm(post):
    return datetime.strptime(post.get('timestamp'), iso_time_format).replace(tzinfo=None)


class InstagramBot:
    def __init__(self, app_data, access_code=None):
        self.insta = InstagramBasicDisplay(**app_data)

        self.saved_token_path = 'hidden/access_token.py'

        self.access_token = self.refresh_or_retrieve_access_token(access_token, access_code)
        self.save_access_token()

        self.insta.set_access_token(self.access_token)
        self.username = self.insta.get_user_profile().get('username')

    def refresh_or_retrieve_access_token(self, saved_token, access_code):
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

    def retrieve_access_token(self, access_code):
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

    def refresh_access_token(self, token) -> str:
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
        Saves access token into 'hidden/access_token.py' which can be imported and used as variable
        """
        with open(self.saved_token_path, 'w') as out:
            out.write(f'access_token = {self.access_token}\n')

    def download_photos_from_post(self, post, post_id=None) -> int:
        """
        Requires access token
        Downloads all photos from posts
        Saves photos as 'username-post_id' for single photo in post and 'username-post_id-i' for carousel

        :param post: post
        :param post_id: extra suffix
        :return: number of downloaded photos
        """
        media_type = post.get('media_type')
        extra = post_id or post.get('id')

        if media_type == 'IMAGE':
            url = post.get('media_url')
            download_jpg_by_url(url, f'{self.username}-{extra}')
            return 1
        elif media_type == 'CAROUSEL_ALBUM':
            data = post.get('children').get('data')
            for i, image_media in enumerate(data, 1):
                self.download_photos_from_post(image_media, f'{extra}-{i}')
            return len(data)

    def get_user_posts(self, begin_dttm=None):
        """
        Requires access token
        Gets user posts after date and time if given or all user posts

        :param begin_dttm: begin datetime or None
        """

        posts = self.insta.get_user_media().get('data')

        if not begin_dttm:
            return posts

        return list(filter(lambda post: get_post_dttm(post) >= begin_dttm, posts))

    def _download_user_posts(self, posts):
        """
        Requires access token
        Downloads photos from given user posts

        :param posts: posts
        """
        post_count = len(posts)
        photo_count = 0

        for post in posts:
            photo_count += self.download_photos_from_post(post)

        print(f'Downloaded {photo_count} photos from {post_count} posts')

    def download_user_posts(self, begin_dttm=None):
        """
        Requires access token
        Downloads user posts after date and time if given or all user posts

        :param begin_dttm: begin datetime
        """

        posts = self.get_user_posts(begin_dttm)
        self._download_user_posts(posts)
