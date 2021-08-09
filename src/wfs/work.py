from helpers import regexes, general, info


class Work:
    fycws_keys = ['formats', 'years', 'creators', 'works', 'sources']
    unwanted_untyped_lines = ['by', 'in', 'the']


    def __init__(self, basis_tag=None, film_title=None, works=None, formats=None, years=None, creators=None, sources=None) -> None:
        self.works = works or []
        self.formats = formats or []
        self.years = years or []
        self.creators = creators or []
        self.sources = sources or []
        if basis_tag:
            self.extract_attrs(basis_tag, film_title)


    def __str__(self) -> str:
        return_val = ''
        for key in self.fycws_keys:
            return_val += f'{key}: {getattr(self, key)}\n'
        return return_val


    def extract_attrs(self, basis_tag, film_title):
        italics_tags = basis_tag.find_all('i')
        italics = [italic_tag.text for italic_tag in italics_tags]
        quotes = regexes.get_quote_re(basis_tag.text, all=True)
        lines = general.get_details_lines(basis_tag, info.excluded_basis)
        lines_schema = {i: [] for i in range(len(lines))}
        for j, line in enumerate(lines):
            line_fycws = {key: [] for key in self.fycws_keys}
            prev_line = general.get_prev_line(j, lines)
            italic = general.get_elm(italics, line)
            quote = general.get_elm(quotes, line)
            line = general.remove_parens(line)
            if italic:
                italic = general.remove_parens(italic)
                if general.is_preceded_by(prev_line, ' in') or quotes:
                    line_fycws['sources'].append(italic)
                elif italic not in info.work_format_words:
                    line_fycws['works'].append(italic)
            if quote:
                line_fycws['works'].append(quote)
            line_fycws['formats'] = general.get_elms(info.work_format_words, line)
            line_fycws['years'] = regexes.get_year_re(line, all=True)
            if line[:3].lower() == 'by ':
                line_fycws['creators'].append(line[3:])
            if general.is_preceded_by(prev_line, ' by'):
                line_fycws['creators'].append(line)
            for key in self.fycws_keys:
                general.append_unique(line_fycws[key], getattr(self, key), lines_schema, j, key)
        untyped_lines = [lines[key] for key in [*lines_schema] if not lines_schema[key] and lines[key] not in self.unwanted_untyped_lines]
        self.creators.extend(untyped_lines)  # Creator is the only work detail type without something concrete (quotes, italics, enum list, regex) to define it
        if not self.works:
            self.works.append(film_title)
    

    def format_double_creators(self, double_creators, writing):
        for dc in double_creators:
            dc_idx = self.creators.index(dc)
            dc_split = dc.split(' and ')
            if writing:
                writers = [writer.detail for writer in writing]
                writer_creators = [creator for creator in writers if any(partial in creator for partial in dc_split)]
            if writer_creators and len(writer_creators) == 2:
                dc_replacement = writer_creators
            else:
                dc_replacement = dc_split
            self.creators[dc_idx] = dc_replacement[0]
            if len(self.creators) > dc_idx + 1:
                self.creators[dc_idx + 1:dc_idx + 1] = dc_replacement[1:]
            else:
                self.creators.extend(dc_replacement[1:])
