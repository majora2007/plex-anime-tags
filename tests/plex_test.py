import unittest
import plex

class Test_TestPlex(unittest.TestCase):
    
    
    def test_load_allowed_genres(self):
        self.assertListEqual(plex.Plex().load_allowed_genres()[:1], ['mecha'])
    
    def test_load_genre_maps(self):
        self.assertListEqual(plex.Plex().load_genre_maps()[:1], [('past', 'historical')])
    
    