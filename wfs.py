import re
import json
from googlesearch import search
import requests
from bs4 import BeautifulSoup

headers = {
    'Access-Control-Allow-Origin': "*", 'Access-Control-Allow-Methods': "GET", 'Access-Control-Allow-Headers': "Content-Type",
    'Access-Control-Max-Age': "3600", 'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
}

work_format_words = ['novelette', 'novella', 'novel', 'teleplay', 'play', 'short story', 'story', 'book series',
                     'radio series', 'series', 'serial']


def get_film_data():
    with open('./scraper/films_artblog.json', encoding='ISO-8859-1') as f:
        return json.load(f)


def find_film(lst, film):
    for i in lst:
        if i['name'].lower() == film.lower():
            return i


def get_film_page(film, get_local=False, get_all=False):
    if get_all:
        datum_film = film
    elif get_local:
        with open(f'./scraper/html_files/{film}.html', 'r', encoding='utf-8') as f:
            return f.read()
    else:
        data = get_film_data()
        datum_film = find_film(data, film)
    if datum_film:
        search_results = search(f"{datum_film['name']} {datum_film['year']} film wikipedia", stop=5)
        req = requests.get(list(search_results)[0], headers)
        return req.content


def get_infobox_get_cast_heading(soup):
    infobox_table = soup.find('table', class_='infobox vevent')
    cast_heading = soup.find(id='Cast')
    toc_tag = soup.find(id='toc')

    if toc_tag:
        toc = toc_tag.text
        if 'film version' in toc.lower():
            film_version_section = soup.find(id='Film_version')
            infobox_table = film_version_section.find_next('table', class_='infobox vevent')
            cast_heading = film_version_section.find_next('span', string='Cast')

    return infobox_table, cast_heading


def index_of(val, in_list):
    try:
        return in_list.index(val)
    except ValueError:
        pass


def at_index(idx, in_list):
    try:
        return in_list[idx]
    except IndexError:
        pass


def get_elm(targets, line):
    if targets:
        for elm in targets:
            if elm in line:
                return elm


def get_elms(targets, line):
    elms = []
    for elm in targets:
        if elm in line.lower():
            elms.append(elm)
    return elms


def append_unique(appendants, target, schema, idx, line_type):
    if appendants:
        schema[idx].append(line_type)
        for appendant in appendants:
            if appendant not in target:
                target.append(appendant)


def get_prev_line(idx, lines):
    if idx > 0:
        return lines[idx - 1]


def is_preceded_by(prev_line, word):
    if prev_line:
        return (len(prev_line) > len(word) and prev_line[-len(word):] == word) or prev_line == word.strip()


def remove_parens(line):
    if line[0] == '(' and line[-1] == ')':
        return line[1:-1]
    else:
        return line


def update_schema(line, targets, schema, i, line_type):
    if line in targets:
        schema[i] = line_type


def get_parens_re(line: str, start=False, end=False):
    if start:
        return re.match(r'\([^\)]+\)', line)
    elif end:
        return re.search(r'\([^\)]+\)$', line)
    else:
        return re.search(r'\([^\)]+\)', line)


def get_footnote_re(line: str, as_line=False):
    if as_line:
        return re.match(r'\[[^\]]+\]$', line)
    else:
        return re.search(r'\[[^\]]+\]', line)


def get_isodate_re(line: str):
    return re.match(r'\d{4,4}\-\d{2,2}(\-\d{2,2})?$', line)


def get_quote_re(line: str):
    return re.search(r'\"[^\"]+\"', line)


def get_year_res(line: str):
    return re.findall(r'\d{4,4}', line)


class FilmEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


class Work:
    def __init__(self, basis_tag=None, lines=None, film_title=None, work=None, formats=None, years=None, creators=None, sources=None) -> None:
        self.work = work
        self.formats = formats or []
        self.years = years or []
        self.creators = creators or []
        self.sources = sources or []
        if basis_tag:
            self.extract_attrs(basis_tag, lines, film_title)


    def extract_attrs(self, basis_tag, lines, film_title):
        italics = []
        italics_tags = basis_tag.find_all('i')
        if italics_tags:
            italics.extend([italic_tag.text for italic_tag in italics_tags])
            for italic in italics:
                if italic[0] == '(' and italic[-1] == ')':
                    italic = italic[1:-1]
        quote = ''
        quote_re = get_quote_re(basis_tag.text)
        if quote_re:
            quote = quote_re.group()[1:-1]
        lines_schema = {}
        for i in range(len(lines)):
            lines_schema[i] = []

        for i in range(-1, len(lines) - 1):
            next_line = at_index(i + 1, lines)
            if next_line[0] == '(':
                next_line = next_line[1:]
            if next_line[-1] == ')':
                next_line = next_line[:-1]
            formats = get_elms(work_format_words, next_line)
            years = get_year_res(next_line)
            append_unique(formats, self.formats, lines_schema, i + 1, 'formats')
            append_unique(years, self.years, lines_schema, i + 1, 'years')

            this_line = get_prev_line(i + 1, lines)
            is_by_line = next_line[:3].lower() == 'by '
            if is_by_line or (this_line and is_preceded_by(this_line, ' by')):
                self.creators.append(next_line.replace('by ', ''))
                lines_schema[i + 1].append('creators')

            next_line_quote = get_elm([quote], next_line)
            if next_line_quote:
                self.work = next_line_quote
                lines_schema[i + 1].append('work')

            next_line_italic = get_elm(italics, next_line)
            if next_line_italic:
                if is_preceded_by(this_line, ' in') or quote:
                    self.sources.append(next_line_italic)
                    lines_schema[i + 1].append('sources')
                elif next_line_italic not in work_format_words:
                    self.work = next_line_italic
                    lines_schema[i + 1].append('work')

            # Using a line pattern to deduce the information type of a line of unknown type. Example: Scarlet Street
            prev_prev_line_types = lines_schema.get(i - 2)
            prev_line_types = lines_schema.get(i - 1)
            next_line_types = lines_schema.get(i + 1)
            this_line_types = lines_schema.get(i)
            if prev_prev_line_types and prev_line_types and next_line_types and not this_line_types:
                if prev_line_types == next_line_types:
                    for line_type in prev_prev_line_types:
                        getattr(self, line_type).append(this_line)
        
        if not self.work:
            self.work = film_title


class Detail:
    def __init__(self, line=None, detail=None, note=None) -> None:
        self.detail = detail
        self.notes = []
        if note:
            self.notes.append(note)
        if line:
            self.set_detail_set_notes(line)


    def set_detail_set_notes(self, line):
        parens_re = get_parens_re(line)
        while parens_re:
            parens = parens_re.group()
            self.notes.append(parens[1:-1].strip())
            line = line.replace(parens, '').strip()
            parens_re = get_parens_re(line)
        self.detail = line


    def split_actor_detail(self, li):
        dividers = [' as ', ' - ', ' – ']
        divider = get_elm(dividers, self.detail)
        link = li.find('a')
        if link:
            link_text = link.text.strip()
        if divider:
            [name, role] = [elm.strip() for elm in self.detail.split(divider)]
            self.detail = name
            self.role = role
        elif link and index_of(link_text, self.detail) == 0:
            self.role = self.detail.replace(link_text, '').strip()
            self.detail = link_text


class Film:
    def __init__(self, soup) -> None:
        page_title = soup.title.text
        if len(page_title) > 12:
            page_title = page_title[:-12]
        self.titles = [Detail(line=page_title, note='page')]
        self.cast = []


    def set_titles(self, soup):
        summary_tag = soup.find('p', class_='')
        if not summary_tag:
            return
        summary = summary_tag.text.strip()
        print(summary[:100])
        first_i_tag = summary_tag.find('i')
        if not first_i_tag:
            b_tag = summary_tag.find('b')
            if b_tag:
                self.titles.append(Detail(detail=b_tag.text.strip(), note='bold'))
            else:
                self.titles.append(Detail(detail=summary[:50], note='summary'))
            return

        main_title = first_i_tag.text.strip()
        self.titles.append(Detail(detail=main_title, note='main'))
        main_title_parens_re = get_parens_re(summary[len(main_title) + 1:], start=True)
        if main_title_parens_re:
            next_i_tag = first_i_tag.find_next('i')
            if next_i_tag:
                next_i = next_i_tag.text.strip()
                while next_i in main_title_parens_re.group():
                    self.titles.append(Detail(detail=next_i, note='alt'))
                    next_i_tag = next_i_tag.find_next('i')
                    next_i = next_i_tag.text.strip()


    def set_cast(self, cast_heading):
        first_ul = cast_heading.find_next('ul')
        if not first_ul:
            return
        uls = []
        first_ul_parent = first_ul.parent
        if first_ul_parent.name == 'td':  # Example case: Caged
            uls.extend(first_ul.find_previous('tr').find_all('ul'))
        else:
            uls.append(first_ul)
        
        for ul in uls:
            lis = ul.find_all('li', recursive=False)
            # The recursive=False option prevents nested lis from getting their own item in the list, 
            # which would be duplicative due to their inclusion in the text of their parent (see note below)

            for li in lis:
                li_text = li.text.strip()
                footnote_re = get_footnote_re(li_text)
                while footnote_re:
                    li_text = li_text.replace(footnote_re.group(), '').strip()
                    footnote_re = get_footnote_re(li_text)

                if '\n' in li_text:  # Example case: The Lady from Shanghai
                    li_text = li_text.replace('\n', ' (').strip() + ')'
                # When accessing the text property of an li tag that includes a nested list,
                # Beautiful Soup appends the text of its child lis to it, separating them with \n.
                # The operation above should enclose the text of a nested li in parens, which will then be converted into a note.

                credit = Detail(line=li_text)
                credit.split_actor_detail(li)
                self.cast.append(credit)


    def set_infobox_details(self, infobox):
        labels_mapping_table = {
            'Screenplay by': "writing", 'Written by': "writing", 'Story by': "writing", 'Language': "languages",
            'Country': "country", 'Directed by': "direction", 'Edited by': "editing", 'Produced by': "production",
            'Productioncompanies': "production", 'Productioncompany': "production", 'Distributed by': "distribution",
            'Music by': "music", 'Running time': "length", 'Based on': "basis", 'Cinematography': "cinematography", 
            'Box office': "sales", 'Budget': "budget", 'Release date': "dates"
        }

        label_tags = infobox.find_all('th', class_='infobox-label')

        for label_tag in label_tags:
            label = label_tag.text.strip()
            if label not in [*labels_mapping_table]:
                continue
            label = labels_mapping_table[label]
            details_tag = label_tag.find_next('td')
            lines = [str(line) for line in details_tag.stripped_strings if line != '"']

            if label == 'basis':
                self.basis = Work(details_tag, lines, self.titles[0].detail)
                continue
            else:
                setattr(self, label, [])
                credits = getattr(self, label)
            i = 0
            while i < len(lines):
                if lines[i][-1] == ':':
                    note = lines.pop(i)[:-1].lower()
                    for j in range(i, len(lines)):
                        lines[j] += f'({note})'
                while i + 1 < len(lines) and lines[i + 1][0] == '(':
                    lines[i] += lines.pop(i + 1)
                    while lines[i][-1] != ')':
                        try:
                            lines[i] += ' ' + lines.pop(i + 1)
                        except IndexError:
                            lines[i] += ')'
                if lines[i][0] not in [',', '[']:
                    credits.append(Detail(line=lines[i]))
                i += 1


def add_films(films_lookup=None, get_local=False, get_all=False):
    films = []
    if get_all:
        films_lookup = get_film_data()
    for film_lookup in films_lookup:
        film_page = get_film_page(film=film_lookup, get_local=get_local, get_all=get_all)
        if not film_page:
            continue
        film_page_soup = BeautifulSoup(film_page, 'html.parser')
        film = Film(film_page_soup)
        film.set_titles(film_page_soup)
        infobox_table, cast_heading = get_infobox_get_cast_heading(film_page_soup)
        if cast_heading:
            film.set_cast(cast_heading)
        elif infobox_table:
            starring_tag = infobox_table.find('th', string="Starring")
            if starring_tag:
                starring_strings = starring_tag.find_next('td').stripped_strings
                for actor in starring_strings:
                    film.cast.append(Detail(line=str(actor)))

        film.set_infobox_details(infobox_table)
        if getattr(film, 'writing', None) and not getattr(film, 'basis', None):
            creators = list(filter(lambda x: any(note in work_format_words for note in x.notes), film.writing))
            if creators:
                formats = [creator.notes for creator in creators]
                setattr(film, 'basis', Work(creators=[creator.detail for creator in creators], work=film.titles[0].detail, formats=[note for creator in creators for note in creator.notes]))

        films.append(film)

    if not films:
        return
    with open('./scraper/test2.json', 'w', encoding='utf-8') as test:
        json.dump(films, test, ensure_ascii=False, cls=FilmEncoder)


films_test = ["the_killers", "scarlet_street", "too_late_for_tears", "the_reckless_moment", "the_pawnbroker", "the_lady_from_shanghai", "la_nuit_du_carrefour"]
add_films(films_lookup=films_test, get_local=True)
