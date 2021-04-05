from datetime import datetime, timezone


class Channel:
    def __init__(self, id: int, last_update: datetime = None):
        self.id = id
        self.last_update = last_update

    def update(self):
        dttm = self.last_update
        self.last_update = datetime.utcnow().replace(tzinfo=timezone.utc)
        return dttm
