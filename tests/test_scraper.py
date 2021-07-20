import os
import inspect
import sys

tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
wiki_film_scraper_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(wiki_film_scraper_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs.wfs import Scraper
test_scraper = Scraper(choices=['scarlet street'], from_local=True)
test_scraper.set_soups()
print(test_scraper.soups[0].title)
