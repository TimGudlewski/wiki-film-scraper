from helpers import regexes, general


class Detail:
    def __init__(self, raw_detail=None, detail=None, note=None, is_actor=False) -> None:
        self.detail = detail
        self.notes = []
        if note:
            self.notes.append(note)
        if raw_detail:
            self.set_detail_set_notes(raw_detail, is_actor)


    def __eq__(self, o: object) -> bool:
        return self.detail == o.detail


    def set_detail_set_notes(self, raw_detail, is_actor):
        parens_re = regexes.get_parens_re(raw_detail)
        raw_detail_copy = raw_detail
        while parens_re:
            parens = parens_re.group(1)
            year_re = regexes.get_year_re(line=parens, as_line=True)
            if year_re and is_actor:  # A parenthetical note in an actor detail containing only a year will most likely refer to a different film mentioned in a longform commentary on the actor's role in the film the page is about (example case: The Deer Hunter). Such a note would not make sense to add to the 'notes' list of the detail itself.
                raw_detail_copy = raw_detail_copy[parens_re.end():]
            else:
                self.notes.append(parens.strip())
                raw_detail = raw_detail_copy = raw_detail[:parens_re.start()].strip() + raw_detail[parens_re.end():]
            parens_re = regexes.get_parens_re(raw_detail_copy)
        self.detail = raw_detail


    def split_actor_detail(self, li):
        dividers = [' as ', ' - ', ' – ']
        divider = general.get_elm(dividers, self.detail)
        link = li.find('a')
        if link:
            link_text = link.text.strip()
        if divider:
            divider_idx = self.detail.index(divider)
            role_idx = divider_idx + len(divider)
            self.role = self.detail[role_idx:]
            self.detail = self.detail[:divider_idx]
        elif link and general.index_of(link_text, self.detail) == 0:
            self.role = self.detail.replace(link_text, '').strip()
            self.detail = link_text
