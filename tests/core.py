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
from wfs.helpers.general import get_details_tag

writing_labels = ['Screenplay by', 'Written by', 'Story by']
writing_labels_mapping_table = dict.fromkeys(writing_labels, "writing")


class TestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = Scraper(pages_local=True)
        self.film = Film()


    def intra_teardown(self):
        film_attrs = [item for item in dir(self.film) if not (callable(getattr(self.film, item)) or item.startswith('__'))]
        for fa in film_attrs:
            if fa in ['titles', 'cast']:
                while getattr(self.film, fa):
                    getattr(self.film, fa).pop()
            else:
                delattr(self.film, fa)


    def intra_setup_film(self, filename, method, key):
        self.intra_teardown()
        self.scraper._set_soup(filename)
        kwarg = {}
        if method != 'set_titles':
            self.scraper._set_infobox_set_cast_heading()
        else:
            kwarg.update({'hush_sum': True})
        kwarg.update({key: getattr(self.scraper, key)})
        getattr(self.film, method)(**kwarg)


    def intra_setup_work(self, wargs=None, filename=None, call_format=False):
        if not filename:
            self.work = Work(**wargs)
        else:
            self.scraper._set_soup(filename)
            self.film.set_titles(soup=self.scraper.soup)
            self.scraper._set_infobox_set_cast_heading()
            basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
            self.work = Work(basis_tag, self.film.titles[0].detail)
            if call_format:
                and_creators = [creator for creator in self.work.creators if ' and ' in creator]
                if and_creators:
                    self.film.set_infobox_details(infobox=self.scraper.infobox, mapping_table=writing_labels_mapping_table)
                    writing = getattr(self.film, 'writing', None)
                    self.work.format_and_creators(and_creators, writing)
    

    def intra_setup_detail(self, dargs=None, filename=None, call_cast=False, call_infobox=False):
        if not filename:
            self.detail = Detail(**dargs)
        else:
            self.intra_teardown()
            self.scraper._set_soup(filename)
            self.scraper._set_infobox_set_cast_heading()
            if call_cast:
                self.film.set_cast(cast_heading=self.scraper.cast_heading)
            if call_infobox:
                self.film.set_infobox_details(infobox=self.scraper.infobox)
