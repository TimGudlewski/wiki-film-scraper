from helpers import regexes, general, info


class Work:
    
    def __init__(self, basis_tag=None, film_title=None, work=None, formats=None, years=None, creators=None, sources=None) -> None:
        self.work = work
        self.formats = formats or []
        self.years = years or []
        self.creators = creators or []
        self.sources = sources or []
        if basis_tag:
            self.extract_attrs(basis_tag, film_title)


    def extract_attrs(self, basis_tag, film_title):
        italics = []
        italics_tags = basis_tag.find_all('i')
        if italics_tags:
            italics.extend([italic_tag.text for italic_tag in italics_tags])
            for italic in italics:
                if italic[0] == '(' and italic[-1] == ')':
                    italic = italic[1:-1]
        quote = ''
        quote_re = regexes.get_quote_re(basis_tag.text)
        if quote_re:
            quote = quote_re.group(1).strip()

        lines = general.get_details_lines(basis_tag)
        lines_schema = {}
        for i in range(len(lines)):
            lines_schema[i] = []

        for i in range(-1, len(lines) - 1):
            next_line = general.at_index(i + 1, lines)
            if next_line[0] == '(':
                next_line = next_line[1:]
            if next_line[-1] == ')':
                next_line = next_line[:-1]
            formats = general.get_elms(info.work_format_words, next_line)
            years = regexes.get_year_res(next_line)
            general.append_unique(formats, self.formats, lines_schema, i + 1, 'formats')
            general.append_unique(years, self.years, lines_schema, i + 1, 'years')

            this_line = general.get_prev_line(i + 1, lines)
            is_by_line = next_line[:3].lower() == 'by '
            if is_by_line or (this_line and general.is_preceded_by(this_line, ' by')):
                self.creators.append(next_line.replace('by ', ''))
                lines_schema[i + 1].append('creators')

            next_line_quote = general.get_elm([quote], next_line)
            if next_line_quote:
                self.work = next_line_quote
                lines_schema[i + 1].append('work')

            next_line_italic = general.get_elm(italics, next_line)
            if next_line_italic:
                if general.is_preceded_by(this_line, ' in') or quote:
                    self.sources.append(next_line_italic)
                    lines_schema[i + 1].append('sources')
                elif next_line_italic not in info.work_format_words:
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
