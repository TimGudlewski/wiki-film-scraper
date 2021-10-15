from helpers import regexes, general, info


class Work:
    fycws_keys = ['formats', 'years', 'creators', 'works', 'sources']
    unwanted_untyped_lines = ['by', 'in', 'the', 'and', 'or']


    def __init__(self, basis_tag=None, film_title=None, works=None, formats=None, years=None, creators=None, sources=None) -> None:
        self.works = works or []
        self.formats = formats or []
        self.years = years or []
        self.creators = creators or []
        self.sources = sources or []
        self.ft = film_title
        if basis_tag:
            self.extract_attrs(basis_tag, film_title)


    def __str__(self) -> str:
        return_val = ''
        for key in self.fycws_keys:
            if getattr(self, key):
                return_val += f'{key}: {getattr(self, key)}\n'
        return return_val


    def extract_attrs(self, basis_tag, film_title):
        italics_tags = basis_tag.find_all('i')
        italics = [italic_tag.text for italic_tag in italics_tags]
        quotes = regexes.get_quote_re(basis_tag.text, all=True)
        lines = general.get_details_lines(basis_tag, info.excluded_basis)
        lines_schema = {i: [] for i in range(len(lines))}
        for j, line in enumerate(lines):
            print(line)
            line_fycws = {key: [] for key in self.fycws_keys}
            prev_line = general.get_prev_line(j, lines)
            italic = general.get_elm(italics, line)
            quote = general.get_elm(quotes, line)
            line = general.remove_parens(line)
            if italic:
                italic = general.remove_parens(italic)
                if general.is_preceded_by(prev_line, ' in') or quotes:
                    line_fycws['sources'].append(italic)
                elif italic not in info.work_format_words + ['and', 'or']:
                    line_fycws['works'].append(italic)
            if quote:
                line_fycws['works'].append(quote)
            line_fycws['formats'] = general.get_elms(info.work_format_words, line)
            line_fycws['years'] = regexes.get_year_re(line, all=True)
            if line.lower().startswith('by '):
                line_fycws['creators'].append(line[3:])
            if ' by ' in line.lower():
                bindex = line.index(' by ')
                line_fycws['creators'].append(line[bindex + 4:])
            if general.is_preceded_by(prev_line, ' by'):
                line_fycws['creators'].append(line)
            for key in self.fycws_keys:
                general.append_unique(line_fycws[key], getattr(self, key), lines_schema, j, key)
        untyped_lines = [lines[key] for key in lines_schema if not lines_schema[key] and lines[key] not in self.unwanted_untyped_lines]
        self.creators.extend(untyped_lines)  # Creator is the only work detail type without something concrete (quotes, italics, enum list, regex) to define it
        if not self.works:
            self.works.append(film_title)
    

    def format_and_creators(self, writing):
        and_creators = [creator for creator in self.creators if ' and ' in creator]
        for ac in and_creators:
            ac_idx = self.creators.index(ac)
            ac_split = ac.split(' and ')
            writer_creators = []
            if writing:
                writers = [writer.detail for writer in writing]
                writer_creators.extend(creator for creator in writers if any(partial in creator for partial in ac_split))  # Example case: Caged
            if len(writer_creators) == len(ac_split):
                ac_replacement = writer_creators
            else:
                ac_replacement = ac_split
            self.creators[ac_idx] = ac_replacement[0]
            if len(self.creators) > ac_idx + 1:
                self.creators[ac_idx + 1:ac_idx + 1] = ac_replacement[1:]
            else:
                self.creators.extend(ac_replacement[1:])
