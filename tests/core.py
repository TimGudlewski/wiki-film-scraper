import os, inspect, sys, unittest
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.film import Film
from wfs.detail import Detail
from wfs.work import Work


class TestWikiFilm(unittest.TestCase):
    def setUp(self) -> None:
        self.film = Film()
        self.scraper = Scraper(pages_local=True)


    def intra_setup(self, filename, attributes, method, key):
        for attribute in attributes:
            film_attr = getattr(self.film, attribute, None)
            while film_attr:
                film_attr.pop()
        self.scraper._set_soup(filename)
        if method != 'set_titles':
            self.scraper._set_infobox_set_cast_heading()
        kwarg = {key: getattr(self.scraper, key)}
        getattr(self.film, method)(**kwarg)
