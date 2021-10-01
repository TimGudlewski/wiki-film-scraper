from tests.core import *


class TestFilm(TestBase):
    def test_init(self):
        self.assertTrue(type(self.film.titles) is list)
        self.assertEqual(len(self.film.titles), 0)
        self.assertTrue(type(self.film.cast) is list)
        self.assertEqual(len(self.film.cast), 0)
    

    def test_titles(self):
        # Multiple alt titles
        pargs = ['hollow_triumph.html', 'set_titles', 'soup']
        self.intra_setup_film(*pargs)
        self.assertEqual(self.film.titles[0].detail, "Hollow Triumph")
        self.assertEqual(self.film.titles[1].detail, "Hollow Triumph")
        self.assertEqual(self.film.titles[2].detail, "The Man Who Murdered Himself")
        self.assertEqual(self.film.titles[3].detail, "The Scar")
        self.assertListEqual(self.film.titles[0].notes, ["main"])
        self.assertListEqual(self.film.titles[1].notes, ["page"])
        self.assertListEqual(self.film.titles[2].notes, ["alt"])
        self.assertListEqual(self.film.titles[3].notes, ["alt"])
        self.assertEqual(len(self.film.titles), 4)
        # Page parenthetical note
        pargs[0] = 'suddenly.html'
        self.intra_setup_film(*pargs)
        self.assertListEqual(self.film.titles[1].notes, ["page", "1954 film"])
    

    def test_cast(self):
        # Uls in a table
        pargs = ['caged.html', 'set_cast', 'cast_heading']
        self.intra_setup_film(*pargs)
        self.assertEqual(self.film.cast[6].detail, "Jan Sterling")
        self.assertEqual(self.film.cast[6].role, "Jeta Kovsky aka \"Smoochie\"")
        self.assertEqual(len(self.film.cast), 12)
        # Nested lis
        pargs[0] = 'the_lady_from_shanghai.html'
        self.intra_setup_film(*pargs)
        self.assertEqual(self.film.cast[0].detail, "Rita Hayworth")
        self.assertEqual(self.film.cast[0].role, "Elsa \"Rosalie\" Bannister")
        self.assertListEqual(self.film.cast[0].notes, ["singing voice was dubbed by Anita Kert Ellis"])
    

    def test_infobox(self):
        # Normal
        pargs = ['the_seventh_victim.html', 'set_infobox_details', 'infobox']
        self.intra_setup_film(*pargs)
        self.assertEqual(self.film.direction[0].detail, "Mark Robson")
        self.assertListEqual(self.film.direction[0].notes, [])
        # Special method present
        self.assertEqual(self.film.dates[0].detail, "1943-08-21")
        # Special method absent
        for money_label in ['sales', 'budget']:
            self.assertIsNone(getattr(self.film, money_label, None))
        # Multiple parentheticals
        pargs[0] = 'the_pawnbroker.html'
        self.intra_setup_film(*pargs)
        self.assertListEqual(self.film.distribution[1].notes, ["via Republic Pictures", "current"])
        # Spread notes
        pargs[0] = 'the_lady_from_shanghai.html'
        self.intra_setup_film(*pargs)
        for i in range(1, 4):
            self.assertListEqual(self.film.writing[i].notes, ["uncredited"])
