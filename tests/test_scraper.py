import os, inspect, sys, time
from datetime import timedelta

start_time = time.monotonic()

tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
test_scraper = Scraper(choices=['t-men'])
test_scraper.set_films()

end_time = time.monotonic()
print(f'Program Execution Time: {timedelta(seconds=end_time - start_time)}')