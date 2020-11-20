from bson import ObjectId
from typing import List

from .anidb_tag import AniDBTag


class AniDBTitle:
    _id = None  # MongoDB id. Don't rely on this to be populated
    
    def __init__(self, title):
        self.title = title
        self.anidb_id = 0
        self.tags: List[AniDBTag] = []
        self.collections: List[str] = []

    @staticmethod
    def fromJSON(json):
        obj = AniDBTitle(json['title'])

        obj.tags = [AniDBTag(tag['name'], tag['weight']) for tag in json['tags']]
        obj.anidb_id = json['anidb_id']
        obj._id = ObjectId(json['_id'])

        return obj

    def get_db_id(self):
        if isinstance(self._id, str):
            self._id = ObjectId(self._id)

        return self._id

    def __repr__(self):
        return '[AniDBTitle] id: {}, title: {}, genres: {}, collections: {}'.format(self.anidb_id, self.title, self.tags, self.collections)
    
    def __eq__(self, other):
        if isinstance(other, str):
            return self.title.strip() == other.strip()
        else:
            return self.title == other.title and self.anidb_id == other.anidb_id and self.tags == other.tags
                


