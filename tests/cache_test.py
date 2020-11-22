import unittest
from datetime import datetime, timezone, timedelta

import mongomock

from cache import Cache
from models import AniDBTitle, AniDBTag


class Test_TestCache(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = mongomock.MongoClient().db

    def tearDown(self):
        # Clear db
        self.db['cache'].remove({})

    def test_find(self):
        col = self.db['cache']
        anime = AniDBTitle('Some Anime')
        anime.tags = [AniDBTag('fanservice', 200)]

        for obj in [Cache.create_cache_object(anime)]:
            id = col.insert_one(obj).inserted_id

        found_anime = Cache(self.db).find(anime)
        
        self.assertIsNotNone(found_anime)
        self.assertEqual(found_anime._id, id)


    def test_is_expired(self):
        now = datetime.utcnow()

        self.assertTrue(Cache.is_expired(now - timedelta(days=180)))
        self.assertTrue(Cache.is_expired(now - timedelta(days=30)))
        self.assertFalse(Cache.is_expired(now))
    
    def test_update(self):
        col = self.db['cache']
        anime = AniDBTitle('Some Anime 123')
        anime.anidb_id = 2
        anime.tags = [AniDBTag('fanservice', 200)]

        id = col.insert_one(Cache.create_cache_object(anime)).inserted_id

        cache = Cache(self.db)

        anime.anidb_id = 4
        updated_anime = cache.update(anime)

        self.assertEqual(4, updated_anime.anidb_id)


    def test_insert(self):
        col = self.db['cache']
        cache = Cache(self.db)
        anime = AniDBTitle('Some Anime 123')

        updated_anime = cache.update(anime)

        existing_anime = cache.find(anime)

        self.assertEqual(updated_anime, existing_anime)

    
    def refresh(self):
        pass
    
    