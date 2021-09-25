from tests.core import *


class TestFilm(TestWikiFilm):
    def test_init(self):
        self.assertTrue(type(self.film.titles) is list)
        self.assertEqual(len(self.film.titles), 0)
        self.assertTrue(type(self.film.cast) is list)
        self.assertEqual(len(self.film.cast), 0)
    

    def test_titles(self):
        # General and multiple alts
        pargs = ['hollow_triumph.html', ['titles'], 'set_titles', 'soup']
        self.intra_setup(*pargs)
        self.assertEqual(self.film.titles[0].detail, "Hollow Triumph")
        self.assertEqual(self.film.titles[1].detail, "Hollow Triumph")
        self.assertEqual(self.film.titles[2].detail, "The Man Who Murdered Himself")
        self.assertEqual(self.film.titles[3].detail, "The Scar")
        self.assertListEqual(self.film.titles[0].notes, ["main"])
        self.assertListEqual(self.film.titles[1].notes, ["page"])
        self.assertListEqual(self.film.titles[2].notes, ["alt"])
        self.assertListEqual(self.film.titles[3].notes, ["alt"])
        self.assertEqual(len(self.film.titles), 4)
        # Page parenthetical
        pargs[0] = 'suddenly.html'
        self.intra_setup(*pargs)
        self.assertListEqual(self.film.titles[1].notes, ["page", "1954 film"])
    

    def test_cast(self):
        # Uls in a table
        pargs = ['caged.html', ['cast'], 'set_cast', 'cast_heading']
        self.intra_setup(*pargs)
        self.assertEqual(self.film.cast[6].detail, "Jan Sterling")
        self.assertEqual(self.film.cast[6].role, "Jeta Kovsky aka \"Smoochie\"")
        self.assertEqual(len(self.film.cast), 12)
        # Nested lis
        pargs[0] = 'the_lady_from_shanghai.html'
        self.intra_setup(*pargs)
        self.assertEqual(self.film.cast[0].detail, "Rita Hayworth")
        self.assertEqual(self.film.cast[0].role, "Elsa \"Rosalie\" Bannister")
        self.assertListEqual(self.film.cast[0].notes, ["singing voice was dubbed by Anita Kert Ellis"])
    

    def test_infobox(self):
        # Dates
        pargs = ['the_pawnbroker.html', ['dates', 'distribution', 'sales'], 'set_infobox_details', 'infobox']
        self.intra_setup(*pargs)
        self.assertEqual(self.film.dates[0].detail, "1964-06")
        self.assertEqual(self.film.dates[1].detail, "1965-04-20")
        self.assertListEqual(self.film.dates[0].notes, ["Berlin FF"])
        self.assertListEqual(self.film.dates[1].notes, ["U.S."])
        # Multiple parentheticals
        self.assertListEqual(self.film.distribution[1].notes, ["via Republic Pictures", "current"])
        # Money
        self.assertEqual(self.film.sales[0].detail, "$2.5 million")
        self.assertEqual(self.film.sales[0].number, 2500000)
        self.assertListEqual(self.film.sales[0].notes, ["US rentals"])
        pargs[0], pargs[1] = 'the_seventh_victim.html', ['sales', 'budget']
        self.intra_setup(*pargs)
        self.assertListEqual(getattr(self.film, 'sales'), [])
        self.assertListEqual(getattr(self.film, 'budget'), [])
        # Length
        pargs[0], pargs[1] = 'touch_of_evil.html', ['length']
        self.intra_setup(*pargs)
        self.assertEqual(self.film.length[0].detail, "111 minutes")
        self.assertEqual(self.film.length[0].number, 111)
        self.assertListEqual(self.film.length[0].notes, ["1998 version"])
        pargs[0] = 'suddenly.html'
        self.intra_setup(*pargs)
        self.assertEqual(self.film.length[0].detail, "75, 77 or 82 minutes")
        self.assertEqual(self.film.length[0].number, 78)
        self.assertListEqual(self.film.length[0].notes, ["avg"])
        # Spread notes
        pargs[0], pargs[1] = 'the_lady_from_shanghai.html', ['writing']
        self.intra_setup(*pargs)
        self.assertListEqual(self.film.writing[1].notes, ["uncredited"])
        self.assertListEqual(self.film.writing[2].notes, ["uncredited"])
        self.assertListEqual(self.film.writing[3].notes, ["uncredited"])
