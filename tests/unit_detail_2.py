# Run this test from the project root directory
from tests.core import *


class TestDetail(TestBase):
    def test_dunders(self):
        # Init
        self.intra_setup_detail({})
        self.assertIsNone(self.detail.detail)
        self.assertListEqual(self.detail.notes, [])
        self.intra_setup_detail(dict(detail='Hi', note='Bye'))
        self.assertEqual(self.detail.detail, 'Hi')
        self.assertListEqual(self.detail.notes, ['Bye'])
        # Eq
        d1 = self.detail
        self.intra_setup_detail(dict(detail='Hi', note='Cya'))
        self.assertNotEqual(d1.notes[0], self.detail.notes[0])
        self.assertEqual(d1, self.detail)


    def test_set(self):
        # Double parenthetical
        self.intra_setup_detail(filename='the_pawnbroker.html', call_infobox=True)
        self.assertEqual(self.film.distribution[1].detail, "Paramount Pictures")
        self.assertListEqual(self.film.distribution[1].notes, ["via Republic Pictures", "current"])
        # Year note omission
        self.intra_setup_detail(filename='the_deer_hunter.html', call_cast=True)
        self.assertTrue(self.film.cast[4].role.startswith("Linda. Prior to The Deer Hunter, Streep was seen briefly in Fred Zinnemann's Julia (1977)"))
        self.assertListEqual(self.film.cast[4].notes, [])
    

    def test_split(self):
        self.intra_setup_detail(filename='night_and_the_city.html', call_cast=True)
        self.assertEqual(self.film.cast[1].detail, 'Gene Tierney')
        self.assertEqual(self.film.cast[1].role, 'Mary Bristol')
        self.assertListEqual(self.film.cast[1].notes, ['singing voice dubbed by Maudie Edwards'])
        self.assertEqual(self.film.cast[-1].detail, 'Adelaide Hall')
        self.assertListEqual(self.film.cast[-1].notes, ['scenes cut from the final edit'])
        self.assertEqual(self.film.cast[-1].role, '')
    

    def test_dates(self):
        self.intra_setup_detail(filename='the_pawnbroker.html', call_infobox=True)
        self.assertEqual(self.film.dates[0].detail, "1964-06")
        self.assertEqual(self.film.dates[1].detail, "1965-04-20")
        self.assertListEqual(self.film.dates[0].notes, ["Berlin FF"])
        self.assertListEqual(self.film.dates[1].notes, ["U.S."])
    

    def test_money(self):
        self.intra_setup_detail(filename='the_pawnbroker.html', call_infobox=True)
        self.assertEqual(self.film.sales[0].detail, "$2.5 million")
        self.assertEqual(self.film.sales[0].number, 2500000)
        self.assertListEqual(self.film.sales[0].notes, ["US rentals"])
    

    def test_length(self):
        # Parenthetical
        self.intra_setup_detail(filename='touch_of_evil.html', call_infobox=True)
        self.assertEqual(self.film.length[0].detail, "111 minutes")
        self.assertEqual(self.film.length[0].number, 111)
        self.assertListEqual(self.film.length[0].notes, ["1998 version"])
        # Mean
        self.intra_setup_detail(filename='suddenly.html', call_infobox=True)
        self.assertEqual(self.film.length[0].detail, "75, 77 or 82 minutes")
        self.assertEqual(self.film.length[0].number, 78)
        self.assertListEqual(self.film.length[0].notes, ["avg"])
