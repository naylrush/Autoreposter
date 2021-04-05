from datetime import datetime
import urllib.request


class SimplePost:
    def __init__(self, post: dict):
        self.username = post.get('username')
        self.post_id = post.get('id')
        self.dttm = get_post_dttm(post)
        self.caption = post.get('caption')

        media_type = post.get('media_type')

        if media_type == 'IMAGE':
            self.urls = [post.get('media_url')]
        elif media_type == 'CAROUSEL_ALBUM':
            self.urls = []
            data = post.get('children').get('data')
            for image_data in data:
                self.urls.append(image_data.get('media_url'))

    def download_photos(self) -> int:
        """
        Saves photos as 'username-post_id' for single photo in post and 'username-post_id-i' for carousel

        :return: number of downloaded photos
        """
        filename = f'{self.username}-{self.post_id}'

        if len(self.urls) == 1:
            download_jpg_by_url(self.urls[0], filename)
        else:
            for i, url in enumerate(self.urls, 1):
                download_jpg_by_url(url, f'{filename}-{i}')

        return len(self.urls)


iso_time_format = '%Y-%m-%dT%H:%M:%S%z'


def get_post_dttm(post):
    return datetime.strptime(post.get('timestamp'), iso_time_format).replace(tzinfo=None)


def download_jpg_by_url(url, filename):
    with urllib.request.urlopen(url) as photo_raw:
        with open(f'downloads/{filename}.jpg', 'wb') as photo_file:
            photo_file.write(photo_raw.read())
