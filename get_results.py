# -*- coding: utf-8 -*-
import re
import os
import time
import shutil
import logging
import requests

from jinja2 import Environment, FileSystemLoader
from collections import namedtuple

template_directory = './templates/'
www_directory = './www/'
server_url = 'http://localhost:80/'

columns = [
    ['BEGINNERS', 'KIDS', 'MŽ10', 'Ž12', 'M12', 'Ž14', 'M14', 'OPEN'],
    ['Ž16', 'Ž18', 'Ž21B', 'Ž21E', 'Ž35', 'Ž45', 'Ž55', 'Ž65'],
    ['M16', 'M18', 'M21A', 'M21B', 'M21E', 'M35', 'M45', 'M50', 'M55', 'M60', 'M65', 'M70']
]

Runner = namedtuple('Runner', ['place', 'name', 'club', 'time', 'behind'])
Category = namedtuple('Category', ['title', 'runners'])

category_pattern = re.compile(r'<a href="ClassResults\?ID=([0-9]+)" style="text-decoration:none;"><div style="font-size:40px;text-decoration:none;border-top:solid 1px #FFFFFF;width:100%;color:white;padding-top:10px;padding-bottom:10px;">([\w\s]+)</div></a>', re.IGNORECASE)
runner_pattern = re.compile(r'<div style="padding-right:3px;text-align:right;float:left;height:20px;width:35px;padding-top:10px;padding-bottom:10px;font-size:22px">([0-9\.]*)</div>([\w\s]*)<span style="font-size:18px;color:#666666"><br>([\w\s,]*)</span></div><div style="float:right;padding-right:10px;padding-top:10px;padding-bottom:10px;text-align:right;font-size:22px">([\w:]*)<span style="font-size:18px;color:#666666"><br>([\w:]*)</span>', re.IGNORECASE)

THIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), template_directory)
j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def get_categories():
    r = requests.get(server_url + 'index.html')
    category_data = re.findall(category_pattern, r.text)

    logger.info("Categories: {} ".format([category[1] for category in category_data]))

    return category_data


def check_categories(category_data):
    all_categories = set(category[1] for category in category_data)
    in_columns = set(category for column in columns for category in column)
    if all_categories.difference(in_columns):
        logger.info("Missing columns: {}".format(all_categories.difference(in_columns)))
    elif in_columns.difference(all_categories):
        logger.info("Not existing categories: {}".format(in_columns.difference(all_categories)))
    else:
        logger.info("Categories OK")


def get_results(category_data):
    categories_dict = {}
    for category, title in category_data:
        r = requests.get(server_url + 'ClassResults?ID={}'.format(category))
        runners_data = re.findall(runner_pattern, r.text)
        runners = [Runner._make(r) for r in runners_data]
        categories_dict[title] = runners

    return categories_dict


def init_www_directory():
    if not os.path.exists(www_directory):
        os.makedirs(www_directory)
    with open(os.path.join(www_directory, 'main.html'), 'w', encoding='utf-8') as f:
        f.write(j2_env.get_template('main.html').render(columns=columns))

    if not os.path.exists(os.path.join(www_directory, 'css')):
        shutil.copytree(os.path.join(template_directory, 'css'), os.path.join(www_directory, 'css'))
    if not os.path.exists(os.path.join(www_directory, 'js')):
        shutil.copytree(os.path.join(template_directory, 'js'), os.path.join(www_directory, 'js'))
    if not os.path.exists(os.path.join(www_directory, 'fonts')):
        shutil.copytree(os.path.join(template_directory, 'fonts'), os.path.join(www_directory, 'fonts'))

    for i, column in enumerate(columns):
        with open(os.path.join(www_directory, 'frame{}.html'.format(i)), 'w', encoding='utf-8') as f:
            f.write(j2_env.get_template('frame.html').render(i=i))


def refresh_results(category_data):
    categories_dict = get_results(category_data)
    for i, column in enumerate(columns):
        categories = [Category(title=title, runners=categories_dict[title]) for title in column]
        with open(os.path.join(www_directory, 'res{}.html'.format(i)), 'w', encoding='utf-8') as f:
            f.write(j2_env.get_template('result.html').render(categories=categories))


if __name__ == "__main__":
    categories_data = get_categories()
    check_categories(categories_data)
    init_www_directory()
    while True:
        refresh_results(categories_data)
        logger.info("Results refreshed")
        time.sleep(30)
