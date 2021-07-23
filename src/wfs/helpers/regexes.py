import re


def get_parens_re(line: str, start=False, end=False):
    if start:
        return re.match(r'\((.+?)\)', line)
    elif end:
        return re.search(r'\((.+?)\)$', line)
    else:
        return re.search(r'\((.+?)\)', line)


def get_footnote_re(line: str, as_line=False):
    if as_line:
        return re.match(r'\[.+?\]$', line)
    else:
        return re.search(r'\[.+?\]', line)


def get_isodate_re(line: str):
    return re.match(r'\d{4,4}\-\d{2,2}(?:\-\d{2,2})?$', line)


def get_quote_re(line: str):
    return re.search(r'\"(.+?)\"', line)


def get_year_res(line: str):
    return re.findall(r'\d{4,4}', line)
    