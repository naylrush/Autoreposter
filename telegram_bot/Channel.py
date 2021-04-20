from datetime import datetime, timezone


def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


class Channel:
    def __init__(self, id: int, last_update: datetime = None):
        self.id = id
        self.last_update = last_update if last_update else now()

    def update(self):
        dttm, self.last_update = self.last_update, now()
        return dttm
