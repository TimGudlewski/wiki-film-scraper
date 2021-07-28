import os, requests, json, inspect, sys

from helpers.general import depunct, get_details_tag
from googlesearch import search as gsearch
from pathlib import Path
from bs4 import BeautifulSoup
from film import Film
from work import Work
from detail import Detail
from helpers.info import headers, work_format_words, labels_mapping_table

wfs_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class Choice:

    def __init__(self, name: str, year='') -> None:
        self.name = name
        self.year = str(year)
    

    def __str__(self) -> str:
        return f'{self.name} {self.year}'.strip()


class FilmEncoder(json.JSONEncoder):

    def default(self, o):
        return o.__dict__


class Scraper:

    soup  = choices = infobox = cast_heading = None
    films = []


    def __init__(self,
    choices_input = None,
    html_from_file = False,
    query_from_file = False,
    get_all = False,
    query_constructor_path = os.path.join(wfs_dir, 'search', 'films_artblog.json'),
    check_qc_year = False,
    output_path = os.path.join(Path.home(), 'wfs_output', 'example.json'),
    mapping_table = labels_mapping_table,
    html_dir = os.path.join(wfs_dir, 'html')) -> None:
        self.html_from_file = html_from_file
        self.query_from_file = query_from_file
        self.get_all = get_all
        self.query_constructor_path = query_constructor_path
        self.check_qc_year = check_qc_year
        self.output_path = output_path
        self.mapping_table = mapping_table
        self.html_dir = html_dir
        if get_all or choices_input:
            self._set_choices(choices_input)
        else:
            sys.exit('Initialize Scraper instance with a value for choices, or set get_all to True.')


    def _get_query_constructor_file(self):
        with open(self.query_constructor_path, encoding='ISO-8859-1') as f:
            return json.load(f)


    def _get_query_constructor(self, choice, qc_file):
        for qc in qc_file:
            if self.check_qc_year:
                if depunct(qc['name']).lower() == depunct(choice.name).lower() and str(qc['year']) == choice.year:
                    return qc
            else:
                if depunct(qc['name']).lower() == depunct(choice.name).lower():
                    return qc
        sys.exit(f'No query constructor found in QC file for {choice}')


    def _set_choices(self, choices_input):
        if self.html_from_file:
            if self.get_all:
                self.choices = os.listdir(self.html_dir)
            else:
                self.choices = choices_input
        else:
            if self.get_all:
                self.choices = [Choice(**qc) for qc in self._get_query_constructor_file()]
            elif self.query_from_file:
                qc_file = self._get_query_constructor_file()
                qcs = [self._get_query_constructor(choice, qc_file) for choice in choices_input]
                self.choices = [Choice(**qc) for qc in qcs]
            else:
                self.choices = [Choice(**choice) for choice in choices_input]


    def _set_soup(self, choice):
        if self.html_from_file:
            if not self.get_all:
                choice_file = depunct(choice).replace(' ', '_').lower() + '.html'
            else:
                choice_file = choice
            choice_filepath = os.path.join(self.html_dir, choice_file)
            with open(choice_filepath, 'r', encoding='utf-8') as f:
                self.soup = BeautifulSoup(f.read(), 'html.parser')
        else:
            search_results = gsearch(f'{choice} film wikipedia', num_results=1)
            req = requests.get(search_results.pop(0), headers)
            self.soup = BeautifulSoup(req.content, 'html.parser')
            if len(search_results):
                setattr(self, f'{choice} - alt links', search_results)


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


    def set_films(self):
        for choice in self.choices:
            self._set_soup(choice)
            film = Film(self.soup)
            film.set_titles(self.soup)

            self._set_infobox_set_cast_heading()
            if not self.infobox:
                self.films.append(f'No infobox for {choice}')
                continue

            if self.cast_heading:
                film.set_cast(self.cast_heading)
            else:
                starring_tag = self.infobox.find('th', string="Starring")
                if starring_tag:
                    starring_strings = starring_tag.find_next('td').stripped_strings
                    for actor in starring_strings:
                        film.cast.append(Detail(raw_detail=str(actor)))
                else:
                    film.cast = 'No cast heading; no "Starring" label in infobox.'

            film.set_dates(self.infobox)
            film.set_infobox_details(self.infobox, self.mapping_table)
            writing = getattr(film, 'writing', None)
            basis_tag = get_details_tag(self.infobox, 'Based on')
            if basis_tag:
                setattr(film, 'basis', Work(basis_tag, film.titles[0].detail))
                if writing:
                    film.basis.set_complete_creators([writer.detail for writer in writing])
            elif writing:
                creators = list(filter(lambda x: any(note in work_format_words for note in x.notes), writing))
                if creators:
                    work_kwargs = dict(
                        creators = [creator.detail for creator in creators],
                        works = [film.titles[0].detail],
                        formats = [note for creator in creators for note in creator.notes if note in work_format_words]
                        )
                    setattr(film, 'basis', Work(**work_kwargs))
            film.set_money_details(self.infobox)
            self.films.append(film)


    def save_films(self):
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.films, f, ensure_ascii=False, cls=FilmEncoder)
