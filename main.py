import logging
import sys

from plexapi.server import PlexServer
import configparser
import pymongo


from providers import anidb
from plex import Plex
from cache import Cache
from models import AniDBTitle

config_parser = configparser.ConfigParser(interpolation=None)
config_parser.read('settings.ini')
db_client = pymongo.MongoClient(config_parser.get('AniDB', 'cache_mongodb'))
db = db_client['plextags']
anime_cache = Cache(db)

allowed_language_codes = ['en', 'ja', 'x-jat']

logger = logging.getLogger("plex-anime-tags")

def setup_logger():
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler = logging.FileHandler('failed-lookup.log')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.INFO)




if __name__ == '__main__':
    config_parser.read('settings.ini')
    plex = PlexServer(config_parser.get('Plex', 'url'), config_parser.get('Plex', 'token'))
    plex_interface = Plex()
    min_weight = int(config_parser.get('AniDB', 'min_tag_weight'))
    setup_logger()

    titles = []
    anime_library = plex.library.section(config_parser.get('Plex', 'anime_library'))
    plex_interface.set_library(anime_library)
    for video in anime_library.search():
        titles.append(AniDBTitle(video.title))
        #plex_interface.add_show(video.title, video)

    for anime in titles:
        print('Processing "{}"'.format(anime.title))

        anime.anidb_id = anidb.find_id(anime)

        if anime.anidb_id == 0:
            print('Could not find AniDB entry. Skipping.')
            logger.info(anime.title)
            continue

        cached_data = anime_cache.find(anime)
        if cached_data is not None and len(cached_data.tags) > 0:
            print('Cached, skipping refresh'.format(anime.title))
            anime = cached_data
        else:
            anidb.fetch_genres(anime, config_parser)
            anime_cache.update(anime)
        try:
            plex_interface.update_plex(anime, min_weight)
        except Exception as e:
            if 'not_found' in str(e):
                print('ERROR: "{}" does not exist on Plex, yet Plex says it does. Please do a scan to refresh.'.format(anime.title))
            else:
                print('ERROR: Exception occurred! Message: ', e)
