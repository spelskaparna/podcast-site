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
    path = os.path.join('content','episode', str(number) +'.md')
    return path

def extract_title(number):
    path = episode_file_path(number)
    pattern = r'{}.*"(.*)"'
    fields = ["name", "occupation", "company"]
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
    title = '{} {} ({} | {})'.format(number, matches['name'], matches['occupation'], matches['company'])
    return title

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
        description = soup.find('div','content')
    return str(description)

def extract_description_text(number):
    path = os.path.join('public','episode', str(number), 'index.html')
    with open(path,'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        description = soup.find('div','content').find('p')
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



