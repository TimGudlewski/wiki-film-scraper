from string import punctuation


def add_colon_notes(lines):
    for i, line in enumerate(lines):
        if line[-1] == ':':
                note = lines.pop(i)[:-1].lower()
                for j in range(i, len(lines)):
                    lines[j] += f'({note})'


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


def depunct(name):
    return name.translate(str.maketrans('', '', punctuation))


def format_isodate(num: str):
    if len(num) == 1:
        num = '0' + num
    return '-' + num


def get_details_tag(infobox, label):
    label_tag = infobox.find('th', class_='infobox-label', string=label)
    if label_tag:
        return label_tag.find_next('td')


def get_details_lines(details_tag, excluded):
    return [str(line) for line in details_tag.stripped_strings if line not in excluded and line[0] != '[']


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