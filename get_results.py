# -*- coding: utf-8 -*-
import requests
import re

server_url = 'http://localhost:80/'
category_pattern = re.compile(r'<a href="ClassResults\?ID=([0-9]+)" style="text-decoration:none;"><div style="font-size:40px;text-decoration:none;border-top:solid 1px #FFFFFF;width:100%;color:white;padding-top:10px;padding-bottom:10px;">([\w\s]+)</div></a>', re.IGNORECASE)
runner_pattern = re.compile(r'<div style="padding-right:3px;text-align:right;float:left;height:20px;width:35px;padding-top:10px;padding-bottom:10px;font-size:22px">([0-9\.]*)</div>([\w\s]*)<span style="font-size:18px;color:#666666"><br>([\w\s,]*)</span></div><div style="float:right;padding-right:10px;padding-top:10px;padding-bottom:10px;text-align:right;font-size:22px">([\w:]*)<span style="font-size:18px;color:#666666"><br>([\w:]*)</span>', re.IGNORECASE)

r = requests.get(server_url + 'index.html')
categories = re.findall(category_pattern, r.text)

for category, title in categories:
    print('ID={} CAT={}'.format(category, title))
    r = requests.get(server_url + 'ClassResults?ID={}'.format(category))
    runners = re.findall(runner_pattern, r.text)
    for runner in runners:
        print(runner)
