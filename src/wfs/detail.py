from helpers import regexes, general

class Detail:
    def __init__(self, line=None, detail=None, note=None) -> None:
        self.detail = detail
        self.notes = []
        if note:
            self.notes.append(note)
        if line:
            self.set_detail_set_notes(line)


    def set_detail_set_notes(self, line):
        parens_re = regexes.get_parens_re(line)
        while parens_re:
            parens = parens_re.group(1).strip()
            self.notes.append(parens.strip())
            line = line.replace(parens_re.group(), '').strip()
            parens_re = regexes.get_parens_re(line)
        self.detail = line


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