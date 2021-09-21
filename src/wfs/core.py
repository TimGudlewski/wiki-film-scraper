import os, requests, json, inspect

from helpers.general import *
from googlesearch import search as gsearch
from warnings import warn
from pathlib import Path
from bs4 import BeautifulSoup
from film import Film
from helpers.exceptions import ChoicesError, PagesError
from work import Work
from detail import Detail
from helpers.info import headers, work_format_words, labels_mapping_table

wfs_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class Choice:
    def __init__(self, name: str, year='') -> None:
        self.name = name
        self.year = str(year)


    def __str__(self) -> str:
        return f'{self.name or ""} {self.year or ""}'.strip()


class FilmEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Scraper:
    soup = choices = infobox = cast_heading = None
    films = []
    search_results = []


    def __init__(self, pages_local=False, pages_dir_path=os.path.join(wfs_dir, 'pages')) -> None:
        self.pages_local = pages_local
        self.pages_dir_path = pages_dir_path
        if pages_local and not os.path.exists(pages_dir_path):
            raise PagesError(f'Pages directory not found at path: {pages_dir_path}')


    def set_choices(self, choices=None, choices_local=False, choices_file_path=os.path.join(wfs_dir, 'choices', 'films_artblog.json')):
        # The choices parameter should be a list of strings or a list of dicts.
        # If choices is a list of dicts, each dict should have a 'name' and a 'year' key with a single string value for each.
        # If pages_local is True, choices_local and choices_file_path will be ignored, and choices must be a list of strings (or omitted).
        # If choices is omitted and choices_local is True, all films from choices_file_path will be searched.
        # if choices is omitted and pages_local is True, all pages from pages_dir will be processed.
        if not (choices or self.pages_local or choices_local):
            raise ChoicesError('If parameter "choices" not present, either pages_local or choices_local must be true.')
        if choices and type(choices) is not list:
            raise TypeError('Parameter "choices" must be a list, and should only contain strings and/or dictionaries.')
        if not self.pages_local:
            if choices_local:
                choices_file = read_json_file(choices_file_path)
                if choices:
                    final_choices = get_file_choices(choices, choices_file, choices_file_path)
                else:
                    final_choices = choices_file
                self.choices = [Choice(name=choice.get('name'), year=choice.get('year')) for choice in final_choices]
            else:
                self.choices = []
                for choice in choices:
                    if type(choice) is dict:
                        self.choices.append(Choice(name=choice.get('name'), year=choice.get('year')))
                    else:
                        if type(choice) is not str:
                            warn('Each choice in "choices" should be of type str or dict.')
                        self.choices.append(str(choice))
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
                return
            with open(page_file_path, 'r', encoding='utf-8') as f:
                self.soup = BeautifulSoup(f.read(), 'html.parser')
        else:
            search_results = gsearch(f'{choice} film wikipedia', num_results=3)
            if not search_results:
                warn(f'No search results found for {choice}.')
                return
            self.search_results.append({'choice': str(choice), 'results': search_results})
            target_result = at_index(results_idx, search_results)
            if not target_result:
                target_result = at_index(0, search_results)
                warn(f'Search results index out of range (results_idx = {results_idx}). Reverted to 0.')
            req = requests.get(target_result, headers)
            self.soup = BeautifulSoup(req.content, 'html.parser')


    def _set_infobox_set_cast_heading(self):
        self.infobox = self.soup.find('table', class_='infobox vevent')
        self.cast_heading = self.soup.find(id='Cast')
        toc_tag = self.soup.find(id='toc')
        if toc_tag:
            toc = toc_tag.text
            if 'film version' in toc.lower():
                film_version_section = self.soup.find(id='Film_version')
                self.infobox = film_version_section.find_next('table', class_='infobox vevent')
                self.cast_heading = film_version_section.find_next('span', string='Cast')


    def set_films(self, results_idx=0, mapping_table=labels_mapping_table):
        for choice in self.choices:
            if not choice:
                continue
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
            if self.cast_heading:
                film.set_cast(cast_heading=self.cast_heading)
            else:
                starring_tag = self.infobox.find('th', string="Starring")
                if starring_tag:
                    starring_strings = starring_tag.find_next('td').stripped_strings
                    for actor in starring_strings:
                        film.cast.append(Detail(raw_detail=str(actor)))
                else:
                    warn(f'Cast could not be set for {film.titles[0].detail}.')
            film.set_dates(infobox=self.infobox)
            film.set_infobox_details(infobox=self.infobox, mapping_table=mapping_table)
            writing = getattr(film, 'writing', None)
            basis_tag = get_details_tag(self.infobox, 'Based on')
            if basis_tag:
                setattr(film, 'basis', Work(basis_tag, film.titles[0].detail))
                and_creators = [creator for creator in film.basis.creators if ' and ' in creator]
                if and_creators:
                    film.basis.format_and_creators(and_creators, writing)
            elif writing:
                creators = list(filter(lambda writer: any(note in work_format_words for note in writer.notes), writing))
                if creators:
                    work_kwargs = dict(
                        creators = [creator.detail for creator in creators],
                        works = [film.titles[0].detail],
                        formats = [note for creator in creators for note in creator.notes if note in work_format_words]
                        )
                    setattr(film, 'basis', Work(**work_kwargs))
            self.films.append(film)


    def save_films(self, output_file=os.path.join(Path.home(), 'wfs_output', 'example.json')):
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        write_json_file(output_file, self.films, FilmEncoder)
