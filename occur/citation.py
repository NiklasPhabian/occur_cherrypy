import datetime
import collections
from das import DAS


class Citation:
    def __init__(self):
        self.subset_params = None
        self.meta = collections.OrderedDict()
        self.meta['author'] = None
        self.meta['creation_date'] = None
        self.meta['title'] = None
        self.meta['version'] = None
        self.meta['institution'] = None
        self.meta['url'] = None
        self.meta['accessed'] = datetime.datetime.now().strftime('%Y-%m-%d')
        self.meta['doi'] = None

    def from_das(self, das_txt):
        das = DAS(das_txt)
        self.meta['institution'] = das.institution
        self.meta['author'] = das.author
        self.meta['creation_date'] = das.date
        self.meta['title'] = das.title

    def add_subset_param_dict(self, subset_params):
        self.subset_params = subset_params        

    def as_text(self):
        cit_text = '{'   
        cit_text += self.meta_text() 
        cit_text += self.subset_text() 
        cit_text += '\n}'
        return cit_text
    
    def subset_text(self):
        if len(self.subset_params)>0:
            subset_text = '\n\tsubsetting: {'            
            for key in self.subset_params:
                subset_text += '\n\t\t'
                subset_text += key
                subset_text += self.subset_params[key]
            subset_text += '\n\t}'
            return subset_text
        else:
            return ''        

    def meta_text(self):
        meta_text = ''
        for key in self.meta:
            if self.meta[key]:                
                meta_text += '\n\t'
                meta_text += key
                meta_text += ': "'
                meta_text += self.meta[key]
                meta_text += '",'
        meta_text = meta_text[:-1]        
        return str(meta_text)

    def as_html(self):
        text = self.as_text()
        html = text.replace('\n', '<br>')
        return html

    def as_json(self):
        pass