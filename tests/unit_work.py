import os, inspect, sys, unittest
tests_dir = os.path.abspath(inspect.getfile(inspect.currentframe()))
expected_dir = os.path.join(tests_dir, 'expected_work')
project_dir = os.path.dirname(os.path.dirname(tests_dir))
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.work import Work
from wfs.helpers.general import read_json_file, write_json_file

page_filenames = [
    'the_deer_hunter.html',
    'caged.html',
    'the_lady_from_shanghai.html',
    'the_seventh_victim.html',
    'raw_deal.html'
]