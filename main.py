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
    for video in anime_library.search():
        titles.append(AniDBTitle(video.title))
        plex_interface.add_show(video.title, video)

    #titles = titles[0:25]

    # TODO: Should I move the titles loop into anime_library.search() so the video connection can be cleaned up faster
    for anime in titles:
        print('Processing "{}"'.format(anime.title))

        anime.anidb_id = anidb.find_id(anime)

        if anime.anidb_id == 0:
            print('Could not find AniDB entry. Skipping.')
            logger.info(anime.title)
            continue

        cached_data = anime_cache.find(anime)
        if cached_data is not None:
            print('Cached, skipping refresh'.format(anime.title))
            anime = cached_data
        else:
            anidb.fetch_genres(anime, config_parser)
            anime_cache.update(anime)