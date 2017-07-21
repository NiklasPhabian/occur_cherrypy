import re


class DAS:
    def __init__(self, das_txt):
        self.das_txt = das_txt
        self.institution = None
        self.author = None
        self.date = None
        self.title = None
        self.parse()

    def parse(self):
        self.get_institution()
        self.get_author()
        self.get_date()
        self.get_title()

    def get_institution(self):        
        match = re.search(u'(?i)String institution "(.*)";', self.das_txt)
        if match:
            self.institution = match.group(1)

    def get_author(self):
        match = re.search(u'(?i)String author "(.*)";', self.das_txt)
        if match:
            self.author = match.group(1)

    def get_date(self):
        match = re.search(u'(?i)String date_creation "(.*)";', self.das_txt)
        if match:
            self.date = match.group(1)

    
    def get_title(self):
        match = re.search(u'(?i)String filename "(.*)";', self.das_txt)
        if match:
            self.title = match.group(1)
