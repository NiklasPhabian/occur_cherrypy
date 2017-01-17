import datetime
import collections
from das import DAS


class Citation:
    def __init__(self):
        self.dict = collections.OrderedDict()
        self.dict['author'] = None
        self.dict['creation_date'] = None
        self.dict['title'] = None
        self.dict['version'] = None
        self.dict['institution'] = None
        self.dict['url'] = None
        self.dict['accessed'] = datetime.datetime.now().strftime('%Y-%m-%d')
        self.dict['doi'] = None

    def from_das(self, das_txt):
        das = DAS(das_txt)
        self.dict['institution'] = das.institution
        self.dict['author'] = das.author
        self.dict['creation_date'] = das.date

    def add_subset_param_dict(self, subset_params):
        for key in subset_params:
            self.dict[key] = subset_params[key]

    def as_text(self):
        cit_text = '{'
        for key in self.dict:
            if self.dict[key]:
                cit_text += '\n'
                cit_text += key
                cit_text += ': "'
                cit_text += self.dict[key]
                cit_text += '",'
        cit_text = cit_text[:-1]
        cit_text += '\n}'
        return cit_text

    def as_html(self):
        text = self.as_text()
        html = text.replace('\n', '<br>')
        return html

    def as_json(self):
        pass