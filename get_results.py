# -*- coding: utf-8 -*-
import requests
import re
import os
import shutil
import pickle

from jinja2 import Environment, FileSystemLoader
from collections import namedtuple

Runner = namedtuple('Runner', ['place', 'name', 'club', 'time', 'behind'])
Category = namedtuple('Category', ['title', 'runners'])
template_directory = './templates/'
www_directory = './www/'
server_url = 'http://localhost:80/'
category_pattern = re.compile(r'<a href="ClassResults\?ID=([0-9]+)" style="text-decoration:none;"><div style="font-size:40px;text-decoration:none;border-top:solid 1px #FFFFFF;width:100%;color:white;padding-top:10px;padding-bottom:10px;">([\w\s]+)</div></a>', re.IGNORECASE)
runner_pattern = re.compile(r'<div style="padding-right:3px;text-align:right;float:left;height:20px;width:35px;padding-top:10px;padding-bottom:10px;font-size:22px">([0-9\.]*)</div>([\w\s]*)<span style="font-size:18px;color:#666666"><br>([\w\s,]*)</span></div><div style="float:right;padding-right:10px;padding-top:10px;padding-bottom:10px;text-align:right;font-size:22px">([\w:]*)<span style="font-size:18px;color:#666666"><br>([\w:]*)</span>', re.IGNORECASE)

THIS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), template_directory)
j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

if os.path.exists('./data.p'):
    categories_dict = pickle.load(open('./data.p', 'rb'))
else:
    r = requests.get(server_url + 'index.html')
    category_data = re.findall(category_pattern, r.text)

    categories_dict = {}
    for category, title in category_data:
        r = requests.get(server_url + 'ClassResults?ID={}'.format(category))
        runners_data = re.findall(runner_pattern, r.text)
        runners = [Runner._make(r) for r in runners_data]
        categories_dict[title] = runners

    pickle.dump(categories_dict, open('./data.p', 'wb'))

columns = [
    categories_dict.keys(),
    categories_dict.keys(),
    categories_dict.keys()
]

if not os.path.exists(www_directory):
    os.makedirs(www_directory)

for i, column in enumerate(columns):
    categories = [Category(title=title, runners=categories_dict[title]) for title in column]
    with open(os.path.join(www_directory, 'res{}.html'.format(i)), 'w', encoding='utf-8') as f:
        f.write(j2_env.get_template('result.html').render(categories=categories))
    with open(os.path.join(www_directory, 'frame{}.html'.format(i)), 'w', encoding='utf-8') as f:
        f.write(j2_env.get_template('frame.html').render(i=i))

with open(os.path.join(www_directory, 'main.html'), 'w', encoding='utf-8') as f:
    f.write(j2_env.get_template('main.html').render(columns=columns))

if not os.path.exists(os.path.join(www_directory, 'css')):
    shutil.copytree(os.path.join(template_directory, 'css'), os.path.join(www_directory, 'css'))
if not os.path.exists(os.path.join(www_directory, 'js')):
    shutil.copytree(os.path.join(template_directory, 'js'), os.path.join(www_directory, 'js'))
if not os.path.exists(os.path.join(www_directory, 'fonts')):
    shutil.copytree(os.path.join(template_directory, 'fonts'), os.path.join(www_directory, 'fonts'))

