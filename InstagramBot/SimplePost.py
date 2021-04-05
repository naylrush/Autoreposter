import pathlib
import urllib.request
from datetime import datetime
from typing import List


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

    def download_photos(self) -> List[str]:
        """
        Saves photos as 'username-post_id' for single photo in post and 'username-post_id-i' for carousel

        :return: downloaded photo paths
        """
        if len(self.urls) == 1:
            return [download_jpg_by_url(self.urls[0], f'{self.username}-{self.post_id}')]
        else:
            paths = []
            for i, url in enumerate(self.urls, 1):
                paths.append(download_jpg_by_url(url, f'{self.username}-{self.post_id}-{i}'))
            return paths


iso_time_format = '%Y-%m-%dT%H:%M:%S%z'


def get_post_dttm(post):
    return datetime.strptime(post.get('timestamp'), iso_time_format).replace(tzinfo=None)


working_dir = pathlib.Path().absolute()


def download_jpg_by_url(url, filename):
    """
    :param url: URL
    :param filename: filename whithout .jpg
    :return: path where file was saved
    """
    with urllib.request.urlopen(url) as photo_raw:
        path = f'{working_dir}/downloads/{filename}.jpg'
        with open(path, 'wb') as photo_file:
            photo_file.write(photo_raw.read())
        return path
