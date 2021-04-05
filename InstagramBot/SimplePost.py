import json
import pathlib
import urllib.request
from collections import Counter
from datetime import datetime
from enum import Enum
from typing import List


class MediaType(Enum):
    IMAGE = 0,
    VIDEO = 1

    def extention(self):
        return media_type_extention[self]

    def __str__(self):
        return self.name


media_type_extention = {
    MediaType.IMAGE: 'jpg',
    MediaType.VIDEO: 'mp4'
}


class SimplePost:
    def __init__(self, post: dict):
        self.username = post.get('username')
        self.post_id = post.get('id')
        self.dttm = get_post_dttm(post)
        self.caption = post.get('caption')

        self.urls_types = []

        media_type = post.get('media_type')

        if media_type == 'CAROUSEL_ALBUM':
            data = post.get('children').get('data')
        else:
            data = [post]

        for post in data:
            media_type = MediaType[post.get('media_type')]
            url = post.get('media_url')

            self.urls_types.append((url, media_type))

    def download_content(self) -> (List[str], Counter):
        """
        Saves content as 'username-post_id-i' with correct extention

        :return: paths to downloaded files
        """
        paths = []
        counter = Counter([url_type[1] for url_type in self.urls_types])

        for i, (url, media_type) in enumerate(self.urls_types, 1):
            paths.append(download_file_by_url(url, f'{self.username}-{self.post_id}-{i}.{media_type.extention()}'))
        return paths, counter

    def urlopen_content(self) -> List:
        return [(urllib.request.urlopen(url), media_type) for url, media_type in self.urls_types]

    def __str__(self):
        return json.dumps({
            'username': self.username,
            'post_id': self.post_id,
            'datetime': self.dttm.__str__(),
            'caption': self.caption,
            'urls_types': [(url, media_type.__str__()) for url, media_type in self.urls_types]
        })


iso_time_format = '%Y-%m-%dT%H:%M:%S%z'


def get_post_dttm(post: dict):
    return datetime.strptime(post.get('timestamp'), iso_time_format)


working_dir = pathlib.Path().absolute()


def download_file_by_url(url: str, filename: str):
    """
    :param url:
    :param filename:
    :return: path where file was saved
    """
    with urllib.request.urlopen(url) as file_raw:
        path = f'{working_dir}/downloads/{filename}'
        with open(path, 'wb') as file:
            file.write(file_raw.read())
        return path
