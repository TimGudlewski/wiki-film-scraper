from helpers.regexes import get_footnote_re, get_year_re, get_day_re
from helpers.info import excluded_standard, months
from warnings import warn
import json
from typing import List, Union
from collections.abc import Sequence


def at_index(idx: int, list_or_str: Union[Sequence, str]):
    try:
        return list_or_str[idx]
    except IndexError:
        pass


def get_elm(targets: Sequence, line: str) -> str:
    if targets:
        for elm in targets:
            if elm in line:
                return elm


def spread_notes(lines: Sequence):
    i = 0
    while i < len(lines):
        if lines[i][-1] == ':':
            note = lines.pop(i)[:-1].lower()
            while i < len(lines) and lines[i][-1] != ':':
                lines[i] += f'({note})'
                i += 1
        else:
            i += 1


def depunct(txt: str) -> str:
    from string import punctuation
    punctuation += '–'
    return txt.translate(str.maketrans('', '', punctuation))


def format_isodate_fragment(num: str) -> str:
    if len(num) == 1:
        num = '0' + num
    return '-' + num


def format_isodate(detail: str) -> str:
    month_word = get_elm(months, detail)
    if month_word:
        month = format_isodate_fragment(str(months.index(month_word) + 1))
        year = day = ''
        year_re = get_year_re(detail)
        day_re = get_day_re(detail)
        if year_re:
            year = year_re.group()
        if day_re:
            day = format_isodate_fragment(day_re.group())
        return year + month + day


def read_json_file(path: str):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_all_attrs(obj):
    return [item for item in dir(obj) if not (callable(getattr(obj, item)) or item.startswith('__'))]


def get_details_tag(infobox, label: str):
    label_tag = infobox.find('th', class_='infobox-label', string=label)
    if label_tag:
        return label_tag.find_next('td')


def get_details_lines(details_tag, excluded=excluded_standard) -> List:
    return [str(line) for line in details_tag.stripped_strings if not (line in excluded or get_footnote_re(line, as_line=True))]


def get_elms(targets: Sequence, line: str) -> List:
    elms = []
    for elm in targets:
        if elm in depunct(line.lower()).split():
            elms.append(elm)
    return elms


def get_file_choices(choices: Sequence, file: Sequence, file_path: str) -> List:
    file_choices = []
    for choice in choices:
        if type(choice) is dict:
            file_choices.append(choice)
        else:
            found_file_choice = next((file_choice for file_choice in file if depunct(file_choice['name']).lower() == depunct(str(choice)).lower()), None)
            if not found_file_choice:
                warn(f'No record for {choice} found in {file_path}')
            else:
                file_choices.append(found_file_choice)
    return file_choices


def get_prev_line(idx: int, lines: Sequence):
    if idx > 0:
        return lines[idx - 1]


def index_of(val, in_list: Sequence) -> int:
    try:
        return in_list.index(val)
    except ValueError:
        pass


def is_preceded_by(prev_line: str, word: str) -> bool:
    if prev_line:
        return (len(prev_line) > len(word) and prev_line[-len(word):] == word) or prev_line == word.strip()


def join_parens(lines: Sequence[str]):
    i = 0
    while i < len(lines):
        while i + 1 < len(lines) and lines[i + 1][0] == '(':
            lines[i] += lines.pop(i + 1)
            while lines[i][-1] != ')':
                try:
                    lines[i] += ' ' + lines.pop(i + 1)
                except IndexError:
                    lines[i] += ')'
        i += 1


def remove_enclosures(line: str, encs: Sequence[str]) -> str:
    if line[0] == encs[0] and line[-1] == encs[1]:
        line = line[1:-1]
    return line


def remove_footnotes(li_txt: str) -> str:
    footnote_re = get_footnote_re(li_txt)
    while footnote_re:
        li_txt = li_txt.replace(footnote_re.group(), '').strip()
        footnote_re = get_footnote_re(li_txt)
    return li_txt


def split_actor(li_txt: str, link):
        dividers = [' as ', ' - ', ' – ']
        divider = get_elm(dividers, li_txt)
        if divider:
            divider_idx = li_txt.index(divider)
            role_idx = divider_idx + len(divider)
            role = li_txt[role_idx:]
            name = li_txt[:divider_idx]
        elif link and li_txt.startswith(link.text):
            role = li_txt[len(link.text):].strip()
            name = link.text
        else:
            name = li_txt
            role = ''
        return name, role


def write_json_file(output_file: str, data, encoder):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, cls=encoder)