from helpers import regexes, general
from statistics import mean


class Detail:
    def __init__(self, raw_detail=None, raw_role=None, detail=None, note=None, print_param=False) -> None:
        self.detail = detail
        self.notes = []
        if note:
            self.notes.append(note)
        if raw_detail or raw_role:
            self.set_detail_set_notes([(raw_detail, 'detail'), (raw_role, 'role')], print_param)


    def __eq__(self, o: object) -> bool:
        return self.detail == o.detail


    def set_detail_set_notes(self, raws, print_param):
        for raw_tup in raws:
            if not raw_tup[0]:
                continue
            raw_val, raw_type = raw_tup
            period_parens_re = regexes.get_parens_re(raw_val, with_period=True)
            # Some actor roles contain parentheticals beyond the first sentence which would not make sense to designate as notes. Test case: The Deer Hunter.
            if period_parens_re:
                parens_re = period_parens_re
            else:
                parens_re = regexes.get_parens_re(raw_val, end=True)
            notes = []
            while parens_re:
                parens = parens_re.group(1).strip()
                notes.insert(0, parens)
                if period_parens_re:
                    raw_val = raw_val[:parens_re.start()].strip() + raw_val[parens_re.end() - 1:]
                    break
                else:
                    raw_val = raw_val[:parens_re.start()].strip() + raw_val[parens_re.end():]
                parens_re = regexes.get_parens_re(raw_val, end=True)
            self.notes.extend(notes)
            setattr(self, raw_type, raw_val)


    def remove_year_notes(self):
        i = 0
        while i < len(self.notes):
            year_re = regexes.get_year_re(line=self.notes[i], as_line=True)
            if year_re:
                self.notes.pop(i)
            else:
                i += 1


    def extract_money_num(self):
        money_re = regexes.get_money_re(self.detail)
        if money_re:
            money = float(money_re.group().replace(',', ''))
            if 'million' in self.detail.lower():
                money *= 1000000
            self.number = int(money)
    

    def extract_length_num(self):
        nums = regexes.get_num_re(line=self.detail, all=True)
        if nums:
            num = None
            if len(nums) > 1:
                num = round(mean(int(n) for n in nums))
                self.notes.append('avg')
            else:
                num = int(nums[0])
            self.number = num
    

    def extract_isodate(self):
        is_detail_isodate = False
        i = 0
        while i < len(self.notes):
            note_isodate_re = regexes.get_isodate_re(self.notes[i])
            if note_isodate_re:
                self.detail = note_isodate_re.group()
                is_detail_isodate = True
                self.notes.pop(i)
            else:
                i += 1
        if not is_detail_isodate:
            detail_isodate_re = regexes.get_isodate_re(self.detail)
            if detail_isodate_re:
                self.detail = detail_isodate_re.group()
            else:
                isodate = general.format_isodate(self.detail)
                if isodate:
                    self.detail = isodate
