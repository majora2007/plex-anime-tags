
import configparser
from datetime import datetime, timezone, timedelta

from models import AniDBTitle

config_parser = configparser.ConfigParser(interpolation=None)


class Cache:
    """ Represents a cache for anime data """
    __instance = None
    refresh_days = 30
    
    def __new__(cls, db_connection=None):
        if Cache.__instance is None:
            Cache.__instance = object.__new__(cls)
            Cache.__instance.db_connection = db_connection
        
        return Cache.__instance
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.cache_con = db_connection['cache']

    def find(self, anime: AniDBTitle) -> AniDBTitle:
        """ Checks cache to see if data already existing. If last_updated is later than configured refresh time (30 days default)
        then None will be returned """
        existing_record = self.cache_con.find_one({'title': anime.title})

        if existing_record is not None and existing_record != {} and not Cache.is_expired(existing_record['last_updated']):
            return AniDBTitle.fromJSON(existing_record)
        
        print('{} is not in cache'.format(anime.title))
        return None
    
    def update(self, anime: AniDBTitle) -> AniDBTitle:
        """ For a given anime, insert or update DB entry """
        found_anime = self.find(anime)
        if found_anime is None:
            result = self.cache_con.insert_one(Cache.create_cache_object(anime))
            anime._id = result.inserted_id
        else:
            self.cache_con.update_one({'_id': found_anime.get_db_id()}, {'$set': Cache.create_cache_object(anime)})
            anime._id = found_anime.get_db_id()

        return self.find(anime)
    
    @staticmethod
    def create_cache_object(anime):
        return {
            'title': anime.title,
            'anidb_id': anime.anidb_id,
            'tags': [a.toJSON() for a in anime.tags],
            'last_updated': datetime.now(timezone.utc)
        }

    @staticmethod
    def is_expired(last_updated):
        prev_day = last_updated
        now = datetime.utcnow()

        if isinstance(last_updated, str):
            prev_day = datetime.utcfromtimestamp(int(last_updated))

        if now >= prev_day + timedelta(days=30):
            return True

        return False
    
