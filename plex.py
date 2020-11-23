import csv


def is_field_locked(show, field):
    for field in show.fields:
        if field.name == field:
            return field.locked

    return False


class Plex:
    __instance = None
    allowed_genres = []
    genre_maps = []
    connection_map = {}
    library = None

    def __new__(cls):
        if Plex.__instance is None:
            Plex.__instance = object.__new__(cls)

        return Plex.__instance

    def __init__(self):
        self.load_genre_maps()
        self.load_allowed_genres()

    def set_library(self, anime_library):
        self.library = anime_library

    def load_allowed_genres(self):
        """ loads genres.csv for filtering out AniDB tags """
        if len(self.allowed_genres) > 0:
            return

        with open('data/genres.csv', 'r', newline='', encoding='utf8') as csv_file:
            reader = csv.reader(csv_file, quoting=csv.QUOTE_NONE)

            for row in reader:
                if len(row) == 0 or row[0] == '':
                    continue

                self.allowed_genres.append(row[0].lower().strip())

    def load_genre_maps(self):
        """ loads genres.csv for filtering out AniDB tags """
        if len(self.genre_maps) > 0:
            return

        with open('data/genre_map.csv', 'r', newline='', encoding='utf8') as csv_file:
            reader = csv.reader(csv_file, quoting=csv.QUOTE_NONE)

            for row in reader:
                if len(row) == 0 or row[0] == '':
                    continue

                self.genre_maps.append((row[0].lower().strip(), row[1].lower().strip()))

    def get_connection(self, title):
        return self.library.get(title)

    def update_plex(self, anime, min_weight):
        print('Updating Plex for {}'.format(anime.title))

        if self.library is None:
            raise Exception('No connection to Plex server.')
            return

        show = self.get_connection(anime.title)

        if show is None:
            raise Exception('Could not find Plex connection for this show!')
            return

        plex_genres = [str(x).split(':')[1].replace('>', '') for x in show.genres]
        plex_genres_locked = is_field_locked(show, 'genre')
        approved_tags = [anidb_tag for anidb_tag in anime.tags if int(anidb_tag.weight) > min_weight]

        print('\t\tPlex\'s genres: {}'.format(plex_genres))
        print('\t\tPlex\'s genres locked: {}'.format(plex_genres_locked))
        print('\t\tFetched genres: {}'.format(approved_tags))



        # Only include fetched_genres that match allowed_genres
        filtered_genres = []
        for fetched_genre in approved_tags:
            if fetched_genre.name.lower().strip() in self.allowed_genres:
                filtered_genres.append(fetched_genre.name.lower().strip())

        for existing_genre in plex_genres:
            existing_genre_formatted = existing_genre.lower().strip()
            if existing_genre_formatted in self.allowed_genres and (
                    existing_genre_formatted not in filtered_genres or existing_genre_formatted == 'nudity'):
                filtered_genres.append(existing_genre_formatted)

        # Map genres to target genre
        for genre in filtered_genres:
            index = [i for i, v in enumerate(self.genre_maps) if v[0].lower().strip() == genre]
            if len(index) > 0:
                new_genre = self.genre_maps[index[0]][1]
                update_index = filtered_genres.index(genre)
                filtered_genres[update_index] = new_genre

        # If Plex's genres were locked, ensure all tags are copied over with new tags
        if plex_genres_locked:
            filtered_genres += plex_genres

        filtered_genres = [a.title() for a in filtered_genres]

        # Ensure there are no duplicates due to mapping
        filtered_genres = list(dict.fromkeys(filtered_genres))
        filtered_genres.sort()
        print('\t\tMapping {} to new genres of: {}'.format(anime.title, filtered_genres))

        # Check if anything is actually changing before continuing
        if plex_genres == filtered_genres or len(filtered_genres) == 0:
            print('No update needed. Plex genres match already or nothing new to update.')
            return

        show.removeGenre(plex_genres)
        show.addGenre(filtered_genres)
