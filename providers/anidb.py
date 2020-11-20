import csv
import os
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from models import AniDBTitle, AniDBTag
from . import RateLimited

allowed_language_codes = ['en', 'ja', 'x-jat']


def find_id(anime: AniDBTitle):
    with open(os.path.join(os.getcwd(), 'data/anime-titles.dat'), 'r', newline='', encoding="utf8") as csv_file:
        reader = csv.reader(csv_file, delimiter='|', quoting=csv.QUOTE_NONE)

        next(reader, None)
        next(reader, None)
        next(reader, None)

        for row in reader:
            language_code = row[2]
            anime_title = row[3].lower()

            if language_code not in allowed_language_codes:
                continue

            if anime_title == anime.title.lower():
                print('Matched on {}'.format(anime_title))
                return row[0]

    return 0


@RateLimited(0.2)
def fetch_genres(anime, config_parser):
    timestamp = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print('[{}] Fetching {}'.format(timestamp, anime.title))

    resp = requests.get(
        'http://api.anidb.net:9001/httpapi?protover=1&request=anime&aid={}&clientver={}&client={}'.format(
            anime.anidb_id, config_parser.get('AniDB', 'clientver'), config_parser.get('AniDB', 'client'))).content
    # Parse resp xml to extract genres
    soup = BeautifulSoup(resp, 'xml')

    if soup.find('error'):
        print('Error fetching data:\n{}'.format(resp))
        return

    # Fetch all tags
    for tag in soup.find_all('tag'):
        if int(tag['weight']) > 0:
            anime_tag = AniDBTag(tag.find('name').get_text(), tag['weight'])
            anime.tags.append(anime_tag)