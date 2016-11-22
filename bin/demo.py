# -*- coding: utf-8 -*-
import sys
sys.path.append('../lib')
import os
import requests
from pyquery import PyQuery as pq
from collections import namedtuple
import itertools
import re


class MobboSpider:

    def __init__(self, package_name="cn.homoe.nicefoodbbtan"):
        """init class
        """
        self.base_url = "https://www.mobbo.com"
        self.ios_search_url = "https://www.mobbo.com/iOS/Search/"
        self.android_search_url = ""
        self.package_name = package_name
        self.search_url = self.ios_search_url + self.package_name


    def _request(self, url):
        """
        Keyword Arguments:
        url -- url to crawl
        return -- pyquery obj
        """
        ret = requests.get(url)
        doc = pq(ret.content)
        #doc.xhtml_to_html()
        return doc


    def crawl(self, package_name=None, package_id=None):
        """crawl package info from mobbe, using package_name or package_id
        Keyword Arguments:
        package_name -- (default None)
        package_id   -- (default None)
        return -- crawled info dict
        """
        if package_name:
            self.package_name = package_name
            self.search_url = self.ios_search_url + package_name

        doc = self._request(self.search_url)
        res_list = doc('div.developerApps').children()
        result_list = []

        for res in res_list.items():
            result = {}
            result['package_name'] = self.pacakge_name
            result['href'] = res('a').attr('href')
            result['app_id'] = self._get_app_id(result['href'])
            result['img_url'] = res('a')('img').attr('src')

            result['app_name'] = res('a')('img').siblings().closest('span').text()
            result['scoring_num'] = self._get_scoring_num(res('a').children()('div')('span').text())
            result['score'] = self._get_score(res('a').children()('div')('span').siblings()('div.stars_red.inline-block').find('div').attr.style)
            result['price'] = res('a').children()('div')('span').siblings()('div.price').text()
            detail_url = self.base_url + result['href']
            detail_info = self._parse_detail_page(detail_url)
            result.update(detail_info)
            result_list.append(result)

        return result_list


    def _get_app_id(self, href_str):

        return href_str.split('/')[-1]


    def _get_scoring_num(self, string):

        return re.search("\d+", string).group(0)


    def _get_score(self, string):

        return re.search("\d+", string).group(0)


    def _parse_detail_page(self, detail_url):

        ret = requests.get(detail_url)
        doc = pq(ret.content)
        DetailInfo = namedtuple('DetailInfo', 'author_name , main_cate, cate, app_size, version, required_os, rating')
        info_generator = itertools.chain(
            (item.text() for item in doc('div.info.clearfix')('a').items()),
            (item.text() for item in doc('div.newInnerDetails')('span').items()))

        detail_info = DetailInfo(*info_generator)
        return detail_info._asdict()



if __name__ == "__main__":
    ms = MobboSpider()
