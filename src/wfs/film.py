from detail import Detail
from work import Work
from helpers import regexes, info
from helpers.general import *


class Film:
    def __init__(self) -> None:
        self.titles = []
        self.cast = []


    def set_titles(self, **kwargs):
        soup = kwargs.get('soup')
        page_title = soup.title.text
        if page_title.endswith(' - Wikipedia'):
            page_title = page_title[:-12]
        self.titles.append(Detail(raw_detail=page_title, note='page'))
        summary_tag = soup.find('p', class_='')
        if not summary_tag:
            return
        summary = summary_tag.text.strip()
        if not kwargs.get('hush_sum'):
            print(summary[:100])
        first_i_tag = summary_tag.find('i')
        if not first_i_tag:
            b_tag = summary_tag.find('b')
            if b_tag and b_tag.text in summary[:50]:
                self.titles.append(Detail(detail=b_tag.text.strip(), note='bold'))
            else:
                self.titles.append(Detail(detail=summary[:50], note='summary'))
            return
        main_title = first_i_tag.text.strip()
        self.titles.insert(0, Detail(detail=main_title, note='main'))
        main_title_parens_re = regexes.get_parens_re(summary[len(main_title) + 1:], start=True)
        if main_title_parens_re:
            main_title_parens = main_title_parens_re.group()
            next_i_tag = first_i_tag.find_next('i')
            if next_i_tag:
                next_i = next_i_tag.text.strip()
                while next_i in main_title_parens:
                    self.titles.append(Detail(detail=next_i, note='alt'))
                    main_title_parens = main_title_parens.replace(next_i, '')
                    next_i_tag = next_i_tag.find_next('i')
                    next_i = next_i_tag.text.strip()


    def set_cast_ul(self, **kwargs):
        first_ul = kwargs.get('first_ul')
        uls = []
        ul_parent = first_ul.parent
        if ul_parent.name == 'td':  # Test case: Caged
            uls.extend(first_ul.find_previous('tr').find_all('ul'))
        else:
            uls.append(first_ul)
        for ul in uls:
            lis = ul.find_all('li', recursive=False)
            # The recursive=False option prevents nested lis from getting their own item in the list, which would be duplicative due to their inclusion in the text of their parent (see note below)
            for li in lis:
                li_class = li.attrs.get('class')
                if li_class and li_class[0] == 'mw-empty-elt':  # Test case: The Chase
                    continue
                li_text = li.text.strip()
                footnote_re = regexes.get_footnote_re(li_text)
                while footnote_re:
                    li_text = li_text.replace(footnote_re.group(), '').strip()
                    footnote_re = regexes.get_footnote_re(li_text)
                if '\n' in li_text:  # Test case: The Lady from Shanghai
                    li_text = li_text.replace('\n', ' (').strip() + ')'
                    # When accessing the text property of an li tag that includes a nested list, Beautiful Soup appends the text of its child lis to it, separating them with \n. The operation above should enclose the text of a nested li in parens, which will then be converted into a note.
                actor_detail = Detail(raw_detail=li_text)
                actor_detail.remove_year_notes()
                actor_detail.split_actor_detail(li)
                self.cast.append(actor_detail)


    def set_cast_table(self, **kwargs):  # Test case: Pushover
        cast_table = kwargs.get('cast_table')
        cast_wtables = cast_table.find_all('table', class_='wikitable')
        for wtable in cast_wtables:
            wtable_rows = wtable.find_all('tr')
            for row in wtable_rows:
                row_tds = row.find_all('td')
                if not row_tds:
                    continue
                tds_clean = []
                for td in row_tds:
                    td_italic = td.find('i')
                    if td_italic and td_italic.text != td.text:
                        td_italic.decompose()  # To eliminate extraneous words such as "with" and "introducing," which appear in italics in the Pushover cast table
                    tds_clean.append(td.text.replace('\n', '').strip())
                name, role = tds_clean[:2]
                actor_detail = Detail(raw_detail=name, raw_role=role)
                actor_detail.remove_year_notes()
                self.cast.append(actor_detail)


    def set_infobox_details(self, **kwargs):
        mapping_table = kwargs.get('mapping_table')
        if not mapping_table or type(mapping_table) is not dict:
            mapping_table = info.labels_mapping_table
        elif type(mapping_table) is not dict:
            warn('Parameter "mapping_table" must be of type dict. Reverted to default.')
        infobox = kwargs.get('infobox')
        label_tags = infobox.find_all('th', class_='infobox-label')
        if not label_tags:
            warn(f'No label tags found in infobox for {self.titles[0].detail}.')
            return
        for label_tag in label_tags:
            label = label_tag.text.strip()
            if label not in [*mapping_table]:
                continue
            label = mapping_table[label]
            details_tag = label_tag.find_next('td')
            lines = get_details_lines(details_tag)
            spread_notes(lines)  # In case a note followed by a colon precedes several details to which it should be applied. Test case: The Lady from Shanghai
            join_parens(lines)  # In case a parenthetical note and its parentheses get split up across multiple lines, which happens when the note is a link.
            details = []
            for line in lines:
                print_param = False
                if label == 'distribution':
                    print_param = True
                detail = Detail(raw_detail=line, print_param=print_param)
                if label in info.special_methods:
                    getattr(detail, info.special_methods[label])()
                details.append(detail)
            existing_details = getattr(self, label, None)
            if existing_details:
                existing_details.extend(detail for detail in details if detail not in existing_details)
            else:
                setattr(self, label, details)
    

    def set_basis(self, **kwargs):
        basis_tag = kwargs.get('basis_tag')
        writing = getattr(self, 'writing', None)
        if basis_tag:
            work = Work(basis_tag, self.titles[0].detail)
            work.format_and_creators(writing)
            self.basis = work
        elif writing:  # Test case: La Nuit du Carrefour
            creators = list(filter(lambda writer: any(note in info.work_format_words for note in writer.notes), writing))
            if creators:
                work_kwargs = dict(
                    creators = [creator.detail for creator in creators],
                    works = [self.titles[0].detail],
                    formats = [note for creator in creators for note in creator.notes if note in info.work_format_words]
                    )
                self.basis = Work(**work_kwargs)
