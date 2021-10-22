import os, requests, json, inspect

from helpers.general import *
from googlesearch import search as gsearch
from warnings import warn
from pathlib import Path
from bs4 import BeautifulSoup
from film import Film
from helpers.exceptions import ChoicesError, PagesError
from detail import Detail
from helpers.info import headers, labels_mapping_table

wfs_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class FilmEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Scraper:
    def __init__(self, pages_local=False, pages_dir_path=os.path.join(wfs_dir, 'pages')) -> None:
        self.pages_local = pages_local
        self.pages_dir_path = pages_dir_path
        self.films = []
        self.search_results = []
        if pages_local and not os.path.exists(pages_dir_path):
            raise PagesError(f'Pages directory not found at path: {pages_dir_path}')


    def set_choices(self, choices=None, choices_local=False, choices_file_path=os.path.join(wfs_dir, 'choices', 'films_artblog.json')):
        # The choices parameter must be a list of strings or a list of dicts.
        # If choices is a list of dicts, each dict must have a 'name' and a 'year' key with a single string value for each.
        # If pages_local is True, choices_local and choices_file_path will be ignored, and choices must be a list of strings (or omitted).
        # If choices is omitted and choices_local is True, all films from choices_file_path will be searched.
        # if choices is omitted and pages_local is True, all pages from pages_dir will be processed.
        if not choices and not (self.pages_local or choices_local):
            raise ChoicesError('If parameter "choices" not present, either parameter "pages_local" or "choices_local" must be true.')
        if choices:
            if type(choices) is not list:
                raise TypeError('Parameter "choices" must be a list')
            if any(not (type(choice) is str or type(choice) is dict) for choice in choices):
                raise TypeError('Parameter "choices" must only contain strings and/or dictionaries.')
            if any(type(choice) is dict and (not choice.get('name') or not choice.get('year')) for choice in choices):
                raise ChoicesError('Every list item of type "dict" in parameter "choices" must contain "name" and "year" keys with non-None values')
        if not self.pages_local:
            if choices_local:
                choices_file = read_json_file(choices_file_path)  # helpers.general
                if choices:
                    final_choices = get_file_choices(choices, choices_file, choices_file_path)  # helpers.general
                else:
                    final_choices = choices_file
                self.choices = [dict(name=choice['name'], year=choice['year']) for choice in final_choices]
            else:
                self.choices = []
                for choice in choices:
                    if type(choice) is dict:
                        self.choices.append(dict(name=choice['name'], year=choice['year']))
                    else:
                        self.choices.append(dict(name=choice))
        else:
            if choices:
                self.choices = [depunct(str(choice)).replace(' ', '_').lower() + '.html' for choice in choices]
            else:
                self.choices = os.listdir(self.pages_dir_path)


    def _set_soup(self, choice, results_idx=0):
        if self.pages_local:
            page_file_path = os.path.join(self.pages_dir_path, choice)
            if not os.path.exists(page_file_path):
                warn(f'No page file found at path: {page_file_path}')
            else:
                with open(page_file_path, 'r', encoding='utf-8') as f:
                    self.soup = BeautifulSoup(f.read(), 'html.parser')
        else:
            query = f'{choice["name"]} {choice.get("year") or ""}'.strip()
            search_results = gsearch(f'{query} film wikipedia', num_results=3)  # Google search
            if not search_results:
                warn(f'No search results found for {choice}.')
                return
            self.search_results.append({'choice': str(choice), 'results': search_results})
            target_result = at_index(results_idx, search_results)  # helpers.general
            if not target_result:
                target_result = at_index(0, search_results)
                warn(f'Search results index out of range (results_idx = {results_idx}). Reverted to 0.')
            req = requests.get(target_result, headers)
            self.soup = BeautifulSoup(req.content, 'html.parser')


    def _set_infobox_set_cast_heading(self):
        self.infobox = self.soup.find('table', class_='infobox vevent')
        self.cast_heading = self.soup.find(id='Cast')
        film_version_section = self.soup.find(id='Film_version')
        if film_version_section:
            self.infobox = film_version_section.find_next('table', class_='infobox vevent')
            self.cast_heading = film_version_section.find_next('span', string='Cast')


    def _set_cast_setup(self):
        table = ul = None
        if self.cast_heading:
            ul = self.cast_heading.find_next('ul')
            ul_heading = None
            if ul:
                ul_heading = ul.find_previous('span', class_='mw-headline')
            if ul_heading != self.cast_heading or not ul:
                ul = None
                table = self.cast_heading.find_next('table', role='presentation')
                table_heading = None
                if table:
                    table_heading = table.find_previous('span', class_='mw-headline')
                if table_heading != self.cast_heading or not table:
                    table = None
        return ul, table


    def set_films(self, results_idx=0, mapping_table=labels_mapping_table):
        for choice in self.choices:
            self._set_soup(choice, results_idx)
            if not self.soup:
                warn(f'Soup could not be made for choice: {choice}. Continued to next choice.')
                continue
            self._set_infobox_set_cast_heading()
            if not self.infobox:
                warn(f'No infobox found for choice: {choice}. Continued to next choice.')
                continue
            film = Film()
            film.set_titles(soup=self.soup)
            first_ul, cast_table = self._set_cast_setup()
            if first_ul:
                film.set_cast_ul(first_ul=first_ul)
            elif cast_table:  # Test case: Pushover
                film.set_cast_table(cast_table=cast_table)
            else:  # Test case: La Nuit du Carrefour
                if self.cast_heading:
                    warn(f'No ul or table found under cast heading for {film.titles[0].detail}.')
                starring_tag = get_details_tag(self.infobox, 'Starring')
                if starring_tag:
                    starring_lines = get_details_lines(starring_tag)
                    for line in starring_lines:
                        film.cast.append(Detail(raw_detail=line))
                else:
                    warn(f'Cast could not be set for {film.titles[0].detail}.')
            film.set_infobox_details(infobox=self.infobox, mapping_table=mapping_table)
            basis_tag = get_details_tag(self.infobox, 'Based on')  # helpers.general
            film.set_basis(basis_tag=basis_tag)
            self.films.append(film)


    def save_films(self, output_file=os.path.join(Path.home(), 'wfs_output', 'example.json')):
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        write_json_file(output_file, self.films, FilmEncoder)  # helpers.general
