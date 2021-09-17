import os, inspect, sys, unittest
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.film import Film


def cast_setup(scraper, filename, film):
    while len(film.cast):
        film.cast.pop()
    scraper._set_soup(filename)
    scraper._set_infobox_set_cast_heading()
    film.set_cast(cast_heading=scraper.cast_heading)


class TestFilm(unittest.TestCase):
    def setUp(self) -> None:
        self.film = Film()
        self.scraper = Scraper(pages_local=True)


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
        cast_setup(self.scraper, 'caged.html', self.film)
        truths.append(self.film.cast[6].detail == "Jan Sterling" and self.film.cast[6].role == "Jeta Kovsky aka \"Smoochie\"")
        truths.append(len(self.film.cast) == 12)
        cast_setup(self.scraper, 'the_deer_hunter.html', self.film)
        truths.append(self.film.cast[4].role.startswith("Linda. Prior to The Deer Hunter, Streep was seen briefly in Fred Zinnemann's Julia (1977)"))
        truths.append(len(self.film.cast[4].notes) == 0)
        cast_setup(self.scraper, 'the_lady_from_shanghai.html', self.film)
        truths.append(self.film.cast[0].detail == "Rita Hayworth" and self.film.cast[0].role == "Elsa \"Rosalie\" Bannister")
        truths.append(self.film.cast[0].notes[0] == "singing voice was dubbed by Anita Kert Ellis" and len(self.film.cast[0].notes) == 1)
        self.assertTrue(all(truths))
