from helpers.regexes import get_footnote_re, get_year_re, get_day_re
from helpers.info import excluded_standard, months
from warnings import warn
import json


def append_unique(appendants, target, schema, idx, line_type):
    if appendants:
        schema[idx].append(line_type)
        for appendant in appendants:
            if appendant not in target:
                target.append(appendant)


def at_index(idx, in_list):
    try:
        return in_list[idx]
    except IndexError:
        pass


def spread_notes(lines):
    i = 0
    while i < len(lines):
        if lines[i][-1] == ':':
            note = lines.pop(i)[:-1].lower()
            while i < len(lines) and lines[i][-1] != ':':
                lines[i] += f'({note})'
                i += 1
        else:
            i += 1


def depunct(txt):
    from string import punctuation
    punctuation += '–'
    return txt.translate(str.maketrans('', '', punctuation))


def format_isodate_fragment(num: str):
    if len(num) == 1:
        num = '0' + num
    return '-' + num


def format_isodate(detail):
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


def read_json_file(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def get_details_tag(infobox, label):
    label_tag = infobox.find('th', class_='infobox-label', string=label)
    if label_tag:
        return label_tag.find_next('td')


def get_details_lines(details_tag, excluded=excluded_standard):
    return [str(line) for line in details_tag.stripped_strings if not (line in excluded or get_footnote_re(line, as_line=True))]


def get_elm(targets, line):
    if targets:
        for elm in targets:
            if elm in line:
                return elm


def get_elms(targets, line):
    elms = []
    for elm in targets:
        if elm in depunct(line.lower()).split():
            elms.append(elm)
    return elms


def get_file_choices(choices, file, file_path):
    file_choices = []
    for choice in choices:
        if type(choice) is dict:
            file_choices.append(choice)
        else:
            found_file_choice = next((file_choice for file_choice in file if depunct(file_choice['name']).lower() == depunct(str(choice)).lower()), None)
            if not found_file_choice:
                warn(f'No record for {choice} found in {file_path}')
            file_choices.append(found_file_choice)
    return file_choices


def get_prev_line(idx, lines):
    if idx > 0:
        return lines[idx - 1]


def index_of(val, in_list):
    try:
        return in_list.index(val)
    except ValueError:
        pass


def is_preceded_by(prev_line, word):
    if prev_line:
        return (len(prev_line) > len(word) and prev_line[-len(word):] == word) or prev_line == word.strip()


def join_parens(lines):
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


def remove_parens(line):
    if line[0] == '(':
        line = line[1:]
    if line[-1] == ')':
        line = line[:-1]
    return line


def update_schema(line, targets, schema, i, line_type):
    if line in targets:
        schema[i] = line_type


def write_json_file(output_file, data, encoder):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, cls=encoder)