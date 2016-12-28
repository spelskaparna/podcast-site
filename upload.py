import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os 
import pyautogui
import re
import json
import click
from bs4 import BeautifulSoup


def init_driver():
    driver = webdriver.Chrome()
    driver.wait = WebDriverWait(driver, 0)
    return driver
 
def login_libsyn(login, passwd):
    driver = init_driver()
    driver.get("https://login.libsyn.com/")
    try:
        email = driver.find_element_by_id("email")
        email.send_keys(login)
        pwd = driver.wait.until(EC.element_to_be_clickable(
            (By.NAME, "password")))
        pwd.send_keys(passwd)
        button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type = 'submit']")))
        button.submit()
    except TimeoutException:
        print("Box or Button not found in google.com")
    return driver


def upload(title, description, login, passwd):
    driver = login_libsyn(login, passwd)
    driver.get("https://four.libsyn.com/content_edit/index/mode/episode")

    title_field = driver.wait.until(EC.element_to_be_clickable((By.ID, "item_title")))
    title_field.send_keys(title)

    src_btn = driver.wait.until(EC.element_to_be_clickable((By.ID, "mceu_18")))
    src_btn.click()

    iframe = driver.find_element_by_xpath("//iframe[@src='https://four.libsyn.com/lib/tinymce4_2/js/tinymce/plugins/codemirror/source.html']")
    driver.switch_to.frame(iframe)
    time.sleep(5)
    driver.execute_script('codemirror.getDoc().setValue({})'.format(json.dumps(description)));
    time.sleep(5)
    driver.switch_to.default_content()
    ok_btn = driver.wait.until(EC.element_to_be_clickable((By.ID, "mceu_44")))
    ok_btn.click()

    button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//text()[contains(.,'Add Media File')]/../..")))
    button.click()
    time.sleep(2)
    button = driver.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//text()[contains(.,'Upload from Hard Drive')]/../..")))
    button.click()
 
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

def extract_description(number):
    path = os.path.join('public','episode', str(number), 'index.html')
    with open(path,'rb') as html:
        soup = BeautifulSoup(html, "html.parser")
        description = soup.find('div','content')
    return str(description)

def extract_file_details(title, u, p):
    driver = login_libsyn(u, p)

    driver.get("https://four.libsyn.com/content/previously-published")

    xpath = "//node()[contains(@data-sort-val,'{}')]//text()[contains(.,'Link/Embed')]/../..".format(title)
    btn = driver.find_element_by_xpath(xpath)
    btn.click()
    time.sleep(2)
    url = driver.wait.until(EC.element_to_be_clickable((By.XPATH,"//text()[contains(.,'Direct Download')]/../..//input"))).get_attribute('value')
    dir_url = driver.wait.until(EC.element_to_be_clickable((By.XPATH,"//text()[contains(.,'Libsyn Directory URL')]/../..//input"))).get_attribute('value')
    pattern = r'.*/id/(\d*)'
    libsyn_id = re.compile(pattern).match(dir_url).group(1)
    return url, libsyn_id

def replace(param, value, number):
    regex = r"{}.*=".format(param)
    replacement = f'{param} ="{value}"\n'
    path = episode_file_path(number)
    program = re.compile(regex)
    with open(path,'r') as f:
        newlines = []
        for line in f.readlines():
            if program.match(line):
                newlines.append(replacement)
            else:
                newlines.append(line)
    with open(path, 'w') as f:
        for line in newlines:
            f.write(line)


@click.command() 
@click.option('-u', prompt=True)
@click.option('-p', prompt=True, hide_input=True)
@click.argument('number')
@click.argument('feature')
def start(u, p, number, feature):
    title = extract_title(number)
    if feature == 'extract':
        url, libsyn_id = extract_file_details(title, u, p)
        replace('audiofile', url, number)
        replace('libsynid', libsyn_id, number)
    elif feature == 'upload':
        description = extract_description(number)
        upload(title, description, u, p)
    input("Press Enter to continue...")


if __name__ == "__main__":
    start()
