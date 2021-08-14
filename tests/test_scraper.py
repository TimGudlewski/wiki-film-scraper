import os, inspect, sys, time
from datetime import timedelta
from pathlib import Path

tests_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, 'src')
wfs_dir = os.path.join(src_dir, 'wfs')
sys.path[0:0] = [src_dir, wfs_dir]

from wfs import Scraper
from wfs.helpers.info import labels_mapping_table as lmt

of_default = os.path.join(Path.home(), 'wfs_output', 'example.json')
cf_default = os.path.join(wfs_dir, 'choices', 'films_artblog.json')
pd_default = pages_dir_path=os.path.join(wfs_dir, 'pages')


def main(choices=None, pl=False, cl=False, ri=0, mt=lmt, of=of_default, cf=cf_default, pd=pd_default):
    start_time = time.monotonic()
    test_scraper = Scraper(pages_local=pl, pages_dir_path=pd)
    test_scraper.set_choices(choices=choices, choices_local=cl, choices_file_path=cf)
    test_scraper.set_films(results_idx=ri, mapping_table=mt)
    test_scraper.save_films(output_file=of)
    end_time = time.monotonic()
    delta = timedelta(seconds=end_time - start_time)
    print(f'Program Execution Time for n={len(test_scraper.choices)}: {delta.total_seconds()} seconds')


test_choices = [
    {'name': 'behind green lights', 'year': '1946'},
    {'name': 'opening night', 'year': '1977'}
]
test_choices_cl = [
    'nora prentiss',
    'odd man out',
    'out of the past',
    'drunken angel',
    'la nuit du carrefour'
]
test_choices_pl = [
    'scarlet street',
    'caged',
    'la nuit du carrefour'
]

cl_kwargs = dict(choices = test_choices_cl, cl = True)
pl_kwargs = dict(choices = test_choices_pl, pl = True)
qs_kwargs = dict(choices = test_choices)
gacl_kwargs = dict(cl = True)
gapl_kwargs = dict(pl = True)

main(**cl_kwargs)
