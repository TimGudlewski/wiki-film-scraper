from detail import Detail
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


    def set_cast(self, **kwargs):
        first_ul = kwargs.get('cast_heading').find_next('ul')
        if not first_ul:
            return
        uls = []
        first_ul_parent = first_ul.parent
        if first_ul_parent.name == 'td':  # Test case: Caged
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
                if '\n' in li_text:  # Test case: The Lady from Shanghai
                    li_text = li_text.replace('\n', ' (').strip() + ')'
                # When accessing the text property of an li tag that includes a nested list,
                # Beautiful Soup appends the text of its child lis to it, separating them with \n.
                # The operation above should enclose the text of a nested li in parens, which will then be converted into a note.
                credit = Detail(raw_detail=li_text, is_actor=True)
                credit.split_actor_detail(li)
                self.cast.append(credit)


    def set_infobox_details(self, **kwargs):
        mapping_table = kwargs.get('mapping_table')
        if not mapping_table or type(mapping_table) is not dict:
            mapping_table = info.labels_mapping_table
            warn('Parameter "mapping_table" must be of type dict. Reverted to default.')
        label_tags = kwargs.get('infobox').find_all('th', class_='infobox-label')
        if not label_tags:
            return
        for label_tag in label_tags:
            label = label_tag.text.strip()
            if label not in [*mapping_table]:
                continue
            label = mapping_table[label]
            details_tag = label_tag.find_next('td')
            lines = get_details_lines(details_tag)
            add_colon_notes(lines)
            join_parens(lines)
            details = []
            for line in lines:
                detail = Detail(raw_detail=line)
                if label in info.special_methods:
                    getattr(detail, info.special_methods[label])()
                details.append(detail)
            credit = getattr(self, label, None)
            if credit:
                credit.extend(detail for detail in details if detail not in credit)
            else:
                setattr(self, label, details)
