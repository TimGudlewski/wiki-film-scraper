# Run this test from the project root directory
from tests.core import *

format_filenames = ['caged.html', 'crime_wave.html']
format_creators = [["Bernard C. Schoenfeld", "Virginia Kellogg"], ["John Hawkins", "Ward Hawkins"]]


class TestWork(TestBase):
    def test_init(self):
        self.intra_setup_work({})
        for key in self.work.fycws_keys:
            val = getattr(self.work, key)
            self.assertListEqual(val, [])
        wargs = dict(years=['1989'], works=['Clear and Present Danger'], creators=['Tom Clancy'])
        self.intra_setup_work(wargs)
        for key in wargs:
            self.assertListEqual(getattr(self.work, key), wargs[key])


    def test_str(self):
        self.intra_setup_work(filename='on_dangerous_ground.html')
        self.assertEqual(str(self.work), "formats: ['novel']\ncreators: ['Gerald Butler']\nworks: ['Mad with Much Heart']\n")


    def test_extract(self):
        # Correct separation of sources and formats
        self.intra_setup_work(filename='the_reckless_moment.html')
        self.assertListEqual(self.work.formats, ["story"])
        self.assertListEqual(self.work.sources, ["Ladies Home Journal"])
        # Correct detection of creator without using 'by'
        self.intra_setup_work(filename='scarlet_street.html')
        self.assertEqual(self.work.creators[1], "André Mouézy-Éon")
        self.intra_setup_work(filename='always.html')
        self.assertListEqual(self.work.creators, ["Dalton Trumbo", "Frederick Hazlitt Brennan", "Chandler Sprague", "David Boehm"])
        # Correct handling of missing work title and duplicate years
        self.intra_setup_work(filename='too_late_for_tears.html')
        self.assertListEqual(self.work.works, ["Too Late for Tears"])
        self.assertListEqual(self.work.years, ["1947"])
    

    def test_format(self):
        for i, fn in enumerate(format_filenames):
            self.intra_setup_work(filename=fn)
            self.assertListEqual(self.work.creators, format_creators[i])
