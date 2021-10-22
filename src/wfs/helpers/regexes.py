import re
anchor = r'\Z'


def get_day_re(line: str):
    return re.search(r'\d{1,2}', line)


def get_footnote_re(line: str, as_line=False):
    ex = r'\[.+?\]'
    if as_line:
        return re.match(ex + anchor, line)
    else:
        return re.search(ex, line)


def get_isodate_re(line: str):
    return re.search(r'\d{4,4}\-\d{2,2}(?:\-\d{2,2})?', line)


def get_money_re(line: str):
    return re.search(r'\d[\d\.\,]*', line)


def get_num_re(line: str, as_line=False, all=False):
    ex = r'\d+'
    if as_line:
        return re.match(ex + anchor, line)
    elif all:
        return re.findall(ex, line)
    else:
        return re.search(ex, line)


def get_parens_re(line: str, start=False, end=False, with_period=False):
    if with_period:
        ex = r'\(([^\)]+)\)\.'
    else:
        ex = r'\(([^\)]+)\)'
    if start:
        return re.match(ex, line)
    elif end:
        return re.search(ex + anchor, line)
    else:
        return re.search(ex, line)


def get_quote_re(line: str, all=False):
    ex = r'\"(.+?)\"'
    if all:
        return re.findall(ex, line)
    else:
        return re.search(ex, line)


def get_year_re(line: str, find_all=False, as_line=False):
    ex = r'\d{4,4}'
    if find_all:
        return re.findall(ex, line)
    elif as_line:
        return re.match(ex + anchor, line)
    else:
        return re.search(ex, line)
    