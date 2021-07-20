from string import punctuation


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


def remove_parens(line):
    if line[0] == '(' and line[-1] == ')':
        return line[1:-1]
    else:
        return line


def update_schema(line, targets, schema, i, line_type):
    if line in targets:
        schema[i] = line_type