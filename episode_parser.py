import re
from datetime import datetime
from bs4 import BeautifulSoup
import os 
from html.parser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def episode_file_path(number):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, 'content','episode', str(number) +'.md')
    return path

def extract_title(number):
    name, occupation, company, subtitle = extract_meta_data(number)
    if subtitle:
        title = '{} {} ({})'.format(number, name, subtitle)
    else:
        title = '{} {} ({} | {})'.format(number, name, occupation, company)
    return title



def extract_meta_data(number):
    path = episode_file_path(number)
    pattern = r'{}.*"(.*)"'
    fields = ["name", "occupation", "company", "subtitle"]
    programs = []
    for field in fields:
        program = re.compile(pattern.format(field))
        programs.append((field, program))
       
    matches = {} 
    with open(path,'r') as episode:
        for row in episode:
            for name, program in programs:
                match = program.match(str(row))
                if match:
                    matches[name]= match.group(1)
    name = matches['name']
    subtitle = None
    occupation = None
    company = None
    if 'subtitle' in matches:
        subtitle = matches['subtitle']
    if 'occupation' in matches:
        occupation = matches['occupation']
    if 'company' in matches:
        company = matches['company']
    return name, occupation, company, subtitle

def extract_date(number):
    path = episode_file_path(number)
    pattern = r'date.*?(\d.*)'
    program = re.compile(pattern)
    with open(path,'r') as episode:
        for row in episode:
            match = program.match(row)
            if match:
                date = (match.group(1))
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return dt

def extract_url(number):
    path = episode_file_path(number)
    pattern = r'audiofile.*"(.*)"'
    program = re.compile(pattern)

    with open(path,'r') as episode:
        for row in episode:
            match = program.match(str(row))
            if match:
                url = match.group(1)
    return url

def extract_description(number):
    path = os.path.join('public','episode', str(number), 'index.html')
    with open(path,'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        description = soup.find('article','blog-post')
        [x.decompose() for x in description.findAll('section')]
    string = "\n".join(str(description).split("\n")[1:-1])
    return string

def extract_description_text(number):
    path = os.path.join('public','episode', str(number), 'index.html')
    with open(path,'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        description = soup.find('article','blog-post').find("p")
    return strip_tags(str(description))

def extract_tags(number):
    path = episode_file_path(number)
    pattern = r'tags.*"(.*)"'
    program = re.compile(pattern)

    with open(path,'r') as episode:
        for row in episode:
            match = program.match(str(row))
            if match:
                tags = match.group(1)
    return tags



