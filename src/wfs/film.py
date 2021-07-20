from detail import Detail
from work import Work
from helpers import regexes, info

class Film:
    def __init__(self, soup) -> None:
        page_title = soup.title.text
        if len(page_title) > 12:
            page_title = page_title[:-12]
        self.titles = [Detail(line=page_title, note='page')]
        self.cast = []


    def set_titles(self, soup):
        summary_tag = soup.find('p', class_='')
        if not summary_tag:
            return
        summary = summary_tag.text.strip()
        print(summary[:100])
        first_i_tag = summary_tag.find('i')
        if not first_i_tag:
            b_tag = summary_tag.find('b')
            if b_tag:
                self.titles.append(Detail(detail=b_tag.text.strip(), note='bold'))
            else:
                self.titles.append(Detail(detail=summary[:50], note='summary'))
            return

        main_title = first_i_tag.text.strip()
        self.titles.append(Detail(detail=main_title, note='main'))
        main_title_parens_re = regexes.get_parens_re(summary[len(main_title) + 1:], start=True)
        if main_title_parens_re:
            next_i_tag = first_i_tag.find_next('i')
            if next_i_tag:
                next_i = next_i_tag.text.strip()
                while next_i in main_title_parens_re.group():
                    self.titles.append(Detail(detail=next_i, note='alt'))
                    next_i_tag = next_i_tag.find_next('i')
                    next_i = next_i_tag.text.strip()


    def set_cast(self, cast_heading):
        first_ul = cast_heading.find_next('ul')
        if not first_ul:
            return
        uls = []
        first_ul_parent = first_ul.parent
        if first_ul_parent.name == 'td':  # Example case: Caged
            uls.extend(first_ul.find_previous('tr').find_all('ul'))
        else:
            uls.append(first_ul)
        
        for ul in uls:
            lis = ul.find_all('li', recursive=False)
            # The recursive=False option prevents nested lis from getting their own item in the list, 
            # which would be duplicative due to their inclusion in the text of their parent (see note below)

            for li in lis:
                li_text = li.text.strip()
                footnote_re = regexes.get_footnote_re(li_text)
                while footnote_re:
                    li_text = li_text.replace(footnote_re.group(), '').strip()
                    footnote_re = regexes.get_footnote_re(li_text)

                if '\n' in li_text:  # Example case: The Lady from Shanghai
                    li_text = li_text.replace('\n', ' (').strip() + ')'
                # When accessing the text property of an li tag that includes a nested list,
                # Beautiful Soup appends the text of its child lis to it, separating them with \n.
                # The operation above should enclose the text of a nested li in parens, which will then be converted into a note.

                credit = Detail(line=li_text)
                credit.split_actor_detail(li)
                self.cast.append(credit)


    def set_infobox_details(self, infobox):
        label_tags = infobox.find_all('th', class_='infobox-label')
        for label_tag in label_tags:
            label = label_tag.text.strip()
            if label not in [*info.labels_mapping_table]:
                continue
            label = info.labels_mapping_table[label]
            details_tag = label_tag.find_next('td')
            lines = [str(line) for line in details_tag.stripped_strings if line != '"']

            if label == 'basis':
                self.basis = Work(details_tag, lines, self.titles[0].detail)
                continue
            else:
                setattr(self, label, [])
                credits = getattr(self, label)
            i = 0
            while i < len(lines):
                if lines[i][-1] == ':':
                    note = lines.pop(i)[:-1].lower()
                    for j in range(i, len(lines)):
                        lines[j] += f'({note})'
                while i + 1 < len(lines) and lines[i + 1][0] == '(':
                    lines[i] += lines.pop(i + 1)
                    while lines[i][-1] != ')':
                        try:
                            lines[i] += ' ' + lines.pop(i + 1)
                        except IndexError:
                            lines[i] += ')'
                if lines[i][0] not in [',', '[']:
                    credits.append(Detail(line=lines[i]))
                i += 1