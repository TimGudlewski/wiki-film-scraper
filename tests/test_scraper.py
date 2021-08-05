import os, inspect, sys, time
from datetime import timedelta

tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper


def main(choices):
    start_time = time.monotonic()

    test_scraper = Scraper()
    test_scraper.set_choices(choices=choices, choices_local=True)
    test_scraper.set_films()
    print(test_scraper.search_results)
    test_scraper.save_films()

    end_time = time.monotonic()
    delta = timedelta(seconds=end_time - start_time)
    print(f'Program Execution Time for n={len(test_scraper.choices)}: {delta.total_seconds()} seconds')


test_choices = [
    'nora prentiss',
    'odd man out',
    'out of the past',
    'drunken angel',
    'la nuit du carrefour'
]
main(test_choices)
