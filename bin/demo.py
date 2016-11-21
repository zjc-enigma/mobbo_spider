# -*- coding: utf-8 -*-
import sys
import os
import requests
from pyquery import PyQuery as pq


base_url = "https://www.mobbo.com"
ios_search_url = "https://www.mobbo.com/iOS/Search/"
android_search_url = ""
package_name = "cn.homoe.nicefoodbbtan"


search_url = ios_search_url + package_name
ret = requests.get(search_url)
doc = pq(ret.content)
#doc.xhtml_to_html()


res_list = doc('div.developerApps').children()


def get_app_id(href):
    pass


def get_scoring_num(string):
    pass


def get_score(string):
    pass


def parse_detail_page(detail_url):
    ret = requests.get(detail_url)
    doc = pq(ret.content)
    author_name , main_cate, cate = (item.text() for item in doc('div.info.clearfix')('a').items())
    app_size, version, required_os, rating = (item.text() for item in doc('div.newInnerDetails')('span').items())





for res in res_list.items():
    href = res('a').attr('href')
    img_url = res('a')('img').attr('src')
    app_name = res('a')('img').siblings().closest('span').text()
    scoring_num = res('a').children()('div')('span').text()
    score = res('a').children()('div')('span').siblings()('div.stars_red.inline-block').find('div').attr.style
    price = res('a').children()('div')('span').siblings()('div.price').text()
    detail_url = base_url + href

