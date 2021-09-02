import os, inspect, sys
from unittest import TestCase
tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
expected_file = os.path.join(tests_dir, 'expected_work', 'expected.json')
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

writing_labels_mapping_table = {
    'Screenplay by': "writing",
    'Written by': "writing",
    'Story by': "writing"
}

from wfs import Scraper
from wfs.work import Work
from wfs.film import Film
from wfs.helpers.general import read_json_file, write_json_file, get_details_tag, at_index

page_filenames_extract = [
    'the_reckless_moment.html',
    'scarlet_street.html',
    'always.html',
    'too_late_for_tears.html'
]
page_filenames_format = [
    'caged.html',
    'crime_wave.html'
]


class TestWorkInit(TestCase):
    def test_plain(self):
        work = Work()
        for key in work.fycws_keys:
            val = getattr(work, key)
            self.assertTrue(type(val) is list and len(val) == 0)
    

    def test_params(self):
        work = Work(years=['1989'], works=['Clear and Present Danger'], creators=['Tom Clancy'])
        self.assertTrue(work.years == ['1989'] and work.works == ['Clear and Present Danger'] and work.creators == ['Tom Clancy'])


class TestWorkMethods(TestCase):
    def setUp(self):
        self.scraper = Scraper(pages_local=True)


    def test_str(self):
        self.scraper._set_soup('on_dangerous_ground.html')
        self.scraper._set_infobox_set_cast_heading()
        basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
        expected_str = "formats: ['novel']\ncreators: ['Gerald Butler']\nworks: ['Mad with Much Heart']\n"
        actual_str = str(Work(basis_tag))
        self.assertEqual(expected_str, actual_str)


    def test_extract(self):
        expected = read_json_file(expected_file)
        for i, fn in enumerate(page_filenames_extract):
            self.scraper._set_soup(fn)
            expected_basis = at_index(i, expected)
            if expected_basis and self.scraper.soup.title.text == expected_basis['film']:
                del expected_basis['film']
                self.scraper._set_infobox_set_cast_heading()
                basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
                work = Work(basis_tag, self.scraper.soup.title.text)
                self.assertEqual(work.__dict__, expected_basis)
    

    def test_format(self):
        expected = read_json_file(expected_file)
        for i, fn in enumerate(page_filenames_format):
            self.scraper._set_soup(fn)
            expected_basis = at_index(i + len(page_filenames_extract), expected)
            if expected_basis and self.scraper.soup.title.text == expected_basis['film']:
                del expected_basis['film']
                self.scraper._set_infobox_set_cast_heading()
                basis_tag = get_details_tag(self.scraper.infobox, 'Based on')
                work = Work(basis_tag, self.scraper.soup.title.text)
                and_creators = [creator for creator in work.creators if ' and ' in creator]
                if and_creators:
                    film = Film()
                    film.set_infobox_details(infobox=self.scraper.infobox, mapping_table=writing_labels_mapping_table)
                    writing = getattr(film, 'writing', None)
                    work.format_and_creators(and_creators, writing)
                self.assertEqual(work.__dict__, expected_basis)


def write_expected():
    from wfs import FilmEncoder
    from dictdiffer import diff
    expected = []
    for fn in page_filenames_extract + page_filenames_format:
        scraper = Scraper(pages_local=True)
        scraper._set_soup(fn)
        scraper._set_infobox_set_cast_heading()
        basis_tag = get_details_tag(scraper.infobox, 'Based on')
        work = Work(basis_tag, scraper.soup.title.text)
        and_creators = [creator for creator in work.creators if ' and ' in creator]
        if and_creators:
            film = Film()
            film.set_infobox_details(infobox=scraper.infobox, mapping_table=writing_labels_mapping_table)
            writing = getattr(film, 'writing', None)
            work.format_and_creators(and_creators, writing)
        setattr(work, 'film', scraper.soup.title.text)
        expected.append(work)
    if os.path.exists(expected_file):
        old = read_json_file(expected_file)
        if old:
            for i, old_basis in enumerate(basis for basis in old if type(basis) is dict):
                new_basis = at_index(i, expected)
                if new_basis:
                    if old_basis['film'] == new_basis.film:
                        for dif in list(diff(old_basis, new_basis.__dict__)):         
                            print(dif)
                    else:
                        print(f"Old film: {old_basis['film']}\nNew film: {new_basis.film}")
    write_json_file(expected_file, expected, FilmEncoder)


if __name__ == '__main__':
    write_expected()
