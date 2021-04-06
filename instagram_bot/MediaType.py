from enum import Enum


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
