from helpers import regexes, general


class Detail:

    def __init__(self, raw_detail=None, detail=None, note=None) -> None:
        self.detail = detail
        self.notes = []
        if note:
            self.notes.append(note)
        if raw_detail:
            self.set_detail_set_notes(raw_detail)


    def __eq__(self, o: object) -> bool:
        return self.detail == o.detail


    def set_detail_set_notes(self, raw_detail):
        parens_re = regexes.get_parens_re(raw_detail)
        while parens_re:
            parens = parens_re.group(1).strip()
            self.notes.append(parens.strip())
            raw_detail = raw_detail.replace(parens_re.group(), '').strip()
            parens_re = regexes.get_parens_re(raw_detail)
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
