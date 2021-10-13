import os, inspect, sys
from unittest import TestCase
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
expected_file = os.path.join(tests_dir, 'expected_detail', 'expected.json')
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs.detail import Detail
from wfs import Scraper
from wfs.film import Film


class TestDetailDunders(TestCase):
    def test_init_plain(self):
        detail = Detail()
        self.assertTrue(detail.detail is None and type(detail.notes) is list and len(detail.notes) == 0)
    

    def test_init_params(self):
        detail = Detail(detail='Hi', note='Bye')
        self.assertTrue(detail.detail == 'Hi' and detail.notes == ['Bye'])
    

    def test_eq(self):
        d1 = Detail(detail='Hi', note='Bye')
        d2 = Detail(detail='Hi', note='Cya')
        self.assertEqual(d1, d2)


class TestDetailMethods(TestCase):
    def setUp(self):
        self.scraper = Scraper(pages_local=True)
        self.film = Film()


    def test_set(self):
        self.scraper._set_soup('the_pawnbroker.html')
        self.scraper._set_infobox_set_cast_heading()
        self.film.set_infobox_details(infobox=self.scraper.infobox)
        detail_actual = self.film.distribution[1]
        detail_expected = 'Paramount Pictures'
        notes_expected = ['via Republic Pictures', 'current']
        self.assertTrue(detail_actual.detail == detail_expected and detail_actual.notes == notes_expected)
    

    def test_split(self):
        self.scraper._set_soup('night_and_the_city.html')
        self.scraper._set_infobox_set_cast_heading()
        self.film.set_cast(cast_heading=self.scraper.cast_heading)
        detail_1_actual = self.film.cast[1]
        detail_2_actual = self.film.cast[-1]
        detail_1_expected = 'Gene Tierney'
        notes_1_expected = ['singing voice dubbed by Maudie Edwards']
        role_1_expected = 'Mary Bristol'
        detail_2_expected = 'Adelaide Hall'
        notes_2_expected = ['scenes cut from the final edit']
        truths = [
            detail_1_actual.detail == detail_1_expected,
            detail_1_actual.notes == notes_1_expected,
            detail_1_actual.role == role_1_expected,
            detail_2_actual.detail == detail_2_expected,
            detail_2_actual.notes == notes_2_expected,
            not detail_2_actual.role
            ]
        self.assertTrue(all(truths))