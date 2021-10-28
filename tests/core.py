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
from wfs.helpers.general import get_details_tag, get_all_attrs

writing_labels = ['Screenplay by', 'Written by', 'Story by']
writing_labels_mapping_table = dict.fromkeys(writing_labels, "writing")


class TestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = Scraper(pages_local=True)
        self.film = Film()


    def intra_teardown(self):
        film_attrs = get_all_attrs(self.film)
        for fa in film_attrs:
            if fa in ['titles', 'cast']:
                while getattr(self.film, fa):
                    getattr(self.film, fa).pop()
            else:
                delattr(self.film, fa)


    def intra_setup_film(self, filename):
        self.intra_teardown()
        self.scraper._set_soup(filename)
        self.scraper._set_infobox_set_cast_heading()


    def intra_setup_film_titles(self, filename):
        self.intra_setup_film(filename)
        summary_title, alts = self.scraper._set_titles_setup(hush_sum=True)
        page_title = self.scraper.soup.title.text
        self.film.set_titles(summary_title=summary_title, alts=alts, page_title=page_title)
    

    def intra_setup_film_cast(self, filename, method):
        self.intra_setup_film(filename)
        first_ul, cast_table = self.scraper._set_cast_setup()
        getattr(self.film, method)(first_ul=first_ul, cast_table=cast_table)
    

    def intra_setup_film_infobox(self, filename, mapping_table=None):
        self.intra_setup_film(filename)
        self.film.set_infobox_details(infobox=self.scraper.infobox, mapping_table=mapping_table)


    def intra_setup_film_basis(self, filename):
        self.intra_setup_film(filename)
        self.film.set_titles(page_title=self.scraper.soup.title.text)
        self.film.set_infobox_details(infobox=self.scraper.infobox)
        basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
        self.film.set_basis(basis_tag=basis_tag)


    def intra_setup_work(self, wargs=None, filename=None):
        if not filename:
            self.work = Work(**wargs)
        else:
            self.intra_teardown()
            self.scraper._set_soup(filename)
            self.film.set_titles(page_title=self.scraper.soup.title.text)
            self.scraper._set_infobox_set_cast_heading()
            self.film.set_infobox_details(infobox=self.scraper.infobox)
            basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
            self.film.set_basis(basis_tag=basis_tag)
            self.work = self.film.basis
    

    def intra_setup_detail(self, dargs=None, filename=None, call_cast=False, call_infobox=False):
        if not filename:
            self.detail = Detail(**dargs)
        else:
            self.intra_teardown()
            self.scraper._set_soup(filename)
            self.scraper._set_infobox_set_cast_heading()
            if call_cast:
                first_ul, _ = self.scraper._set_cast_setup()
                self.film.set_cast_ul(first_ul=first_ul)
            if call_infobox:
                self.film.set_infobox_details(infobox=self.scraper.infobox)
