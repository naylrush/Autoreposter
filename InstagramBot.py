from instagram_basic_display.InstagramBasicDisplay import InstagramBasicDisplay
from instagram_basic_display.InstagramBasicDisplayException import InstagramBasicDisplayException
import datetime
import json
import urllib.request


iso_time_format = '%Y-%m-%dT%H:%M:%S%z'


def download_jpg_by_url(url, filename):
    with urllib.request.urlopen(url) as photo_raw:
        with open(f'downloads/{filename}.jpg', 'wb') as photo_file:
            photo_file.write(photo_raw.read())


class InstagramBot:
    def __init__(self, app_data, access_code=None):
        self.insta = InstagramBasicDisplay(**app_data)

        self.saved_token_filename = 'access_token.hidden'

        with open(self.saved_token_filename) as saved_token_json:
            saved_token = json.load(saved_token_json).get('access_token')

        self.access_token = self.refresh_or_retrieve_access_token(saved_token, access_code)
        self.save_access_token()

        self.insta.set_access_token(self.access_token)
        self.username = self.insta.get_user_profile().get('username')

    def refresh_or_retrieve_access_token(self, saved_token, access_code):
        """
        If previously used access token is not None and is still not expired, function returns new access token
        Otherwise, function gets new access token using access code is provided

        :param saved_token: previously used access token
        :param access_code: access code has to be provided to get new access token
        :returns: new access token
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
        :returns: login URL you need to follow
        """
        return self.insta.get_login_url()

    def retrieve_access_token(self, access_code):
        """
        Retrieves and saves access token based on access code

        :returns: access token
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

        :returns: access token
        """
        # Exchange this token for a long lived token (valid for 60 days)
        long_lived_token = self.insta.refresh_token(token)

        print('Access token was successfully refreshed')

        # Get new access token
        return long_lived_token.get('access_token')

    def save_access_token(self):
        """
        Saves access token into 'access_token.hidden' which can be imported and used as variable
        """
        with open(self.saved_token_filename, 'w') as out:
            out.write(json.dumps({'access_token': self.access_token}, indent=4))

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

    def download_all_user_posts(self):
        """
        Requires access token
        Downloads all user photos
        """
        data = self.insta.get_user_media().get('data')

        post_count = len(data)
        photo_count = 0

        for post in data:
            photo_count += self.download_photos_from_post(post)

        print(f'Downloaded {photo_count} photos from {post_count} posts')

    def download_user_posts_after(self, begin_dttm):
        """
        Requires access token
        Downloads all user photos after given date and time
        """

        data = self.insta.get_user_media().get('data')

        post_count = 0
        photo_count = 0

        for post in data:
            post_dttm = datetime.datetime.strptime(post.get('timestamp'), iso_time_format).replace(tzinfo=None)

            if post_dttm >= begin_dttm:
                post_count += 1
                photo_count += self.download_photos_from_post(post)

        print(f'Downloaded {photo_count} photos from {post_count} posts after {begin_dttm}')