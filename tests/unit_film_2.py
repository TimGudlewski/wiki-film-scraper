import os, inspect, sys, unittest
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.film import Film


class TestFilm(unittest.TestCase):
    def setUp(self) -> None:
        self.film = Film()
        self.scraper = Scraper(pages_local=True)
    

    def intra_setup(self, filename, attributes, method, key):
        for attribute in attributes:
            fattr = getattr(self.film, attribute, None)
            while fattr:
                fattr.pop()
        self.scraper._set_soup(filename)
        self.scraper._set_infobox_set_cast_heading()
        kwarg = {key: getattr(self.scraper, key)}
        getattr(self.film, method)(**kwarg)


    def test_titles_init(self):
        self.assertTrue(type(self.film.titles) is list and len(self.film.titles) == 0)

    
    def test_cast_init(self):
        self.assertTrue(type(self.film.cast) is list and len(self.film.cast) == 0)
    

    def test_titles(self):
        self.scraper._set_soup('hollow_triumph.html')
        self.film.set_titles(soup=self.scraper.soup)
        truths = []
        truths.append(self.film.titles[0].detail == self.film.titles[1].detail == "Hollow Triumph")
        truths.append(self.film.titles[2].detail == "The Man Who Murdered Himself")
        truths.append(self.film.titles[3].detail == "The Scar")
        truths.append(self.film.titles[0].notes[0] == "main" and self.film.titles[1].notes[0] == "page")
        truths.append(self.film.titles[2].notes[0] == self.film.titles[3].notes[0] == "alt")
        truths.append(len(self.film.titles[0].notes) == len(self.film.titles[1].notes) == len(self.film.titles[2].notes) == len(self.film.titles[3].notes) == 1)
        truths.append(len(self.film.titles) == 4)
        self.assertTrue(all(truths))
    

    def test_cast(self):
        truths = []
        pargs = ['caged.html', ['cast'], 'set_cast', 'cast_heading']
        self.intra_setup(*pargs)
        truths.append(self.film.cast[6].detail == "Jan Sterling" and self.film.cast[6].role == "Jeta Kovsky aka \"Smoochie\"")
        truths.append(len(self.film.cast) == 12)
        pargs[0] = 'the_deer_hunter.html'
        self.intra_setup(*pargs)
        truths.append(self.film.cast[4].role.startswith("Linda. Prior to The Deer Hunter, Streep was seen briefly in Fred Zinnemann's Julia (1977)"))
        truths.append(len(self.film.cast[4].notes) == 0)
        pargs[0] = 'the_lady_from_shanghai.html'
        self.intra_setup(*pargs)
        truths.append(self.film.cast[0].detail == "Rita Hayworth" and self.film.cast[0].role == "Elsa \"Rosalie\" Bannister")
        truths.append(self.film.cast[0].notes[0] == "singing voice was dubbed by Anita Kert Ellis" and len(self.film.cast[0].notes) == 1)
        self.assertTrue(all(truths))
    

    def test_infobox(self):
        truths = []
        pargs = ['the_pawnbroker.html', ['dates', 'distribution', 'sales'], 'set_infobox_details', 'infobox']
        self.intra_setup(*pargs)
        # Dates
        truths.append(self.film.dates[0].detail == "1964-06" and self.film.dates[1].detail == "1965-04-20")
        truths.append(self.film.dates[0].notes[0] == "Berlin FF" and len(self.film.dates[0].notes) == 1)
        truths.append(self.film.dates[1].notes[0] == "U.S." and len(self.film.dates[1].notes) == 1)
        # Multiple parentheticals
        truths.append(self.film.distribution[1].notes[0] == "via Republic Pictures" and self.film.distribution[1].notes[1] == "current")
        truths.append(len(self.film.distribution[1].notes) == 2)
        # Money
        truths.append(self.film.sales[0].detail == "$2.5 million" and self.film.sales[0].number == 2500000)
        truths.append(self.film.sales[0].notes[0] == "US rentals" and len(self.film.sales[0].notes) == 1)
        pargs[0], pargs[1] = 'the_seventh_victim.html', ['sales', 'budget']
        self.intra_setup(*pargs)
        truths.append(not (getattr(self.film, 'sales', None) or getattr(self.film, 'budget', None)))
        # Length
        pargs[0], pargs[1] = 'touch_of_evil.html', ['length']
        self.intra_setup(*pargs)
        truths.append(self.film.length[0].detail == "111 minutes" and self.film.length[0].number == 111)
        truths.append(self.film.length[0].notes[0] == "1998 version" and len(self.film.length[0].notes) == 1)
        pargs[0] = 'suddenly.html'
        self.intra_setup(*pargs)
        truths.append(self.film.length[0].detail == "75, 77 or 82 minutes" and self.film.length[0].number == 78)
        truths.append(self.film.length[0].notes[0] == "avg" and len(self.film.length[0].notes) == 1)
        # Spread notes
        pargs[0], pargs[1] = 'the_lady_from_shanghai.html', ['writing']
        self.intra_setup(*pargs)
        truths.append(self.film.writing[1].notes[0] == self.film.writing[2].notes[0] == self.film.writing[3].notes[0] == "uncredited")

        self.assertTrue(all(truths))
