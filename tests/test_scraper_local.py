import os, inspect, sys, time
from datetime import timedelta

tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper


def main(choices_options):
    choices_main = []
    for i in range(len(choices_options)):
        choices_main.append(choices_options[i])

        start_time = time.monotonic()

        test_scraper = Scraper(choices=choices_main, from_local=True)
        test_scraper.set_films()
        test_scraper.save_films()

        end_time = time.monotonic()
        print(f'Program Execution Time for n={len(choices_main)}: {timedelta(seconds=end_time - start_time)}')


test_choices_options = [
    'journey into fear',
    'the pawnbroker'
]
main(test_choices_options)
