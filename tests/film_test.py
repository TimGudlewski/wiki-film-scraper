import os, inspect, sys, unittest
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
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
films_kwargs = []
films_methods = []
for fn in page_filenames:
    scraper = Scraper(pages_local=True)
    scraper._set_soup(fn)
    scraper._set_infobox_set_cast_heading()
    films_kwargs.append(dict(soup=scraper.soup, cast_heading=scraper.cast_heading, infobox=scraper.infobox))
    films_methods.append([item for item in dir(Film) if not item.startswith('__')])


class TestFilm(unittest.TestCase):
    def test_film_methods(self):
        for h, film_methods in enumerate(films_methods):
            expected = read_json_file(f'film_test_expected_{h + 1}.json')
            for i, method in enumerate(film_methods):
                film = Film()
                getattr(film, method)(**films_kwargs[h])
                label = next((key for key in film.__dict__ if film.__dict__[key]), None)
                if not label:
                    self.assertTrue(all(not expected[i][exp_label] for exp_label in expected[i]))
                else:
                    for j, detail in enumerate(getattr(film, label)):
                        self.assertEqual(expected[i][label][j], detail.__dict__)


def write_expected():
    from wfs import FilmEncoder
    for i, film_methods in enumerate(films_methods):
        exp_lst = []
        for method in film_methods:
            film = Film()
            getattr(film, method)(**films_kwargs[i])
            exp_lst.append(film)
        write_json_file(f'film_test_expected_{i + 1}.json', exp_lst, FilmEncoder)


if __name__ == '__main__':
    write_expected()
