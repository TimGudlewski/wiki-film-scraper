import os, inspect, sys, unittest
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
expected_dir = os.path.join(tests_dir, 'expected_film')
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.film import Film
from wfs.helpers.general import read_json_file, write_json_file

page_filenames = [
    'the_deer_hunter.html',
    'caged.html',
    'the_lady_from_shanghai.html',
    'the_seventh_victim.html',
    'raw_deal.html'
]
film_methods = [item for item in dir(Film) if not item.startswith('__')]
films_kwargs = []
for fn in page_filenames:
    scraper = Scraper(pages_local=True)
    scraper._set_soup(fn)
    scraper._set_infobox_set_cast_heading()
    films_kwargs.append(dict(soup=scraper.soup, cast_heading=scraper.cast_heading, infobox=scraper.infobox, hush_sum=True))


class TestFilmInit(unittest.TestCase):
    def setUp(self) -> None:
        self.film = Film()

    def test_titles_success(self):
        self.assertTrue(type(self.film.titles) is list and len(self.film.titles) == 0)
    
    def test_titles_failure(self):
        self.assertFalse(type(self.film.titles) is list and len(self.film.titles) == 0)
    
    def test_cast_success(self):
        self.assertTrue(type(self.film.cast) is list and len(self.film.cast) == 0)
    
    def test_cast_failure(self):
        self.assertFalse(type(self.film.cast) is list and len(self.film.cast) == 0)


class TestFilmMethods(unittest.TestCase):
    def setUp(self) -> None:
        self.partial_records = []
        self.expecteds = [read_json_file(os.path.join(expected_dir, f'{i + 1}.json')) for i in range(len(page_filenames))]
        self.labels = []
        for film_kwargs in films_kwargs:
            self.partial_records.append([])
            self.labels.append([])
            for method in film_methods:
                film = Film()
                getattr(film, method)(**film_kwargs)
                self.partial_records[-1].append(film)
                self.labels[-1].append(next((key for key in film.__dict__ if film.__dict__[key]), None))


    def test_no_label_success(self):
        for h, expected in enumerate(self.expecteds):
            for i in range(len(film_methods)):
                if not self.labels[h][i]:
                    self.assertTrue(all(not expected[i][exp_label] for exp_label in expected[i]))


    def test_no_label_failure(self):
        for h, expected in enumerate(self.expecteds):
            for i in range(len(film_methods)):
                if not self.labels[h][i]:
                    self.assertFalse(all(not expected[i][exp_label] for exp_label in expected[i]))


    def test_label_success(self):
        for h, expected in enumerate(self.expecteds):
            for i in range(len(film_methods)):
                if self.labels[h][i]:
                    for j, detail in enumerate(getattr(self.partial_records[h][i], self.labels[h][i])):
                        self.assertTrue(expected[i][self.labels[h][i]][j] == detail.__dict__)
    
    
    def test_label_failure(self):
        for h, expected in enumerate(self.expecteds):
            for i in range(len(film_methods)):
                if self.labels[h][i]:
                    for j, detail in enumerate(getattr(self.partial_records[h][i], self.labels[h][i])):
                        self.assertFalse(expected[i][self.labels[h][i]][j] == detail.__dict__)


def write_expected():
    from wfs import FilmEncoder
    for i, film_kwargs in enumerate(films_kwargs):
        exp_lst = []
        for method in film_methods:
            film = Film()
            getattr(film, method)(**film_kwargs)
            exp_lst.append(film)
        write_json_file(os.path.join(expected_dir, f'{i + 1}.json'), exp_lst, FilmEncoder)


if __name__ == '__main__':
    write_expected()
