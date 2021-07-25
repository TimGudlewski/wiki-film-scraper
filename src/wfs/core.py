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

    def __init__(self, name: str, year=None) -> None:
        self.name = name
        self.year = str(year) or None
    

    def __str__(self) -> str:
        return self.name


class FilmEncoder(json.JSONEncoder):

    def default(self, o):
        return o.__dict__


class Scraper:

    soup = choice = choices = infobox = cast_heading = None
    films = []


    def __init__(self,
    choices_input = None,
    from_local = False,
    get_all = False,
    search_path = os.path.join(wfs_dir, 'search', 'films_artblog.json'),
    output_path = os.path.join(Path.home(), 'wfs_output', 'example.json'),
    mapping_table = labels_mapping_table,
    html_dir = os.path.join(wfs_dir, 'html')) -> None:
        self.from_local = from_local
        self.get_all = get_all
        self.search_path = search_path
        self.output_path = output_path
        self.mapping_table = mapping_table
        self.html_dir = html_dir
        if not choices_input and not get_all:
            msg = "Please initialize Scraper instance with a value for choices, or set get_all to True."
            sys.exit(msg)
        if get_all:
            self._set_choices()
        elif choices_input:
            if isinstance(self.choices[0], dict):
                self.choices = [Choice(**choice) for choice in choices_input]
            else:
                self.choices = choices_input
    

    def _get_search_file(self):
        with open(self.search_path, encoding='ISO-8859-1') as f:
            return json.load(f)


    def _set_choices(self):
        if self.from_local:
            self.choices = os.listdir(self.html_dir)
        else:
            self.choices = self._get_search_file()


    def _set_soup(self):
        if self.from_local:
            if not self.get_all:
                choice_file = depunct(self.choice).replace(' ', '_').lower() + '.html'
            else:
                choice_file = self.choice
            choice_filepath = os.path.join(self.html_dir, choice_file)
            with open(choice_filepath, 'r', encoding='utf-8') as f:
                self.soup = BeautifulSoup(f.read(), 'html.parser')
        else:
            if isinstance(self.choice, Choice):
                search_film = self.choice
            else:
                search_film = Choice(**self._get_search_film())
            query = f"{search_film['name']} {search_film['year']} film wikipedia"
            search_results = gsearch(query, num_results=1)
            print(search_results)
            req = requests.get(search_results.pop(0), headers)
            self.soup = BeautifulSoup(req.content, 'html.parser')
            if len(search_results):
                setattr(self, f"{search_film['name']} - alt links", search_results)
    

    def _get_search_film(self):
        for film in self._get_search_file():
            if depunct(film['name']).lower() == depunct(self.choice).lower():
                return film
        sys.exit()


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
            self.choice = choice
            self._set_soup()
            film = Film(self.soup)
            film.set_titles(self.soup)

            self._set_infobox_set_cast_heading()

            if not self.infobox:
                self.films.append(f'no infobox')
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
                    film.cast = 'no cast heading, no starring in infobox'

            film.set_dates(self.infobox)
            basis_tag = get_details_tag(self.infobox, 'Based on')
            if basis_tag:
                setattr(film, 'basis', Work(basis_tag, film.titles[0].detail))
            film.set_infobox_details(self.infobox, self.mapping_table)
            if getattr(film, 'writing', None) and not getattr(film, 'basis', None):
                creators = list(filter(lambda x: any(note in work_format_words for note in x.notes), film.writing))
                if creators:
                    work_kwargs = dict(
                        creators = [creator.detail for creator in creators],
                        work = film.titles[0].detail,
                        formats = [note for creator in creators for note in creator.notes if note in work_format_words]
                        )
                    setattr(film, 'basis', Work(**work_kwargs))

            self.films.append(film)


    def save_films(self):
        output_dir = os.path.dirname(self.output_path)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(self.films, f, ensure_ascii=False, cls=FilmEncoder)
