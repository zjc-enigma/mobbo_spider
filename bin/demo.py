# -*- coding: utf-8 -*-
import sys
sys.path.append('../lib')
import os
import requests
from pyquery import PyQuery as pq
from collections import namedtuple
import itertools
import re
from search import Google
#import pdb

class MobboSpider:

    def __init__(self, package_name="cn.homoe.nicefoodbbtan"):
        """init class
        """
        self.base_url = "https://www.mobbo.com"
        self.ios_search_url = "https://www.mobbo.com/iOS/Search/"
        self.android_search_url = ""
        self.package_name = package_name
        self.search_url = self.ios_search_url + self.package_name
        self.MAX_ITEM_NUM = 3

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


    def crawl(self, *, package_name=None, package_id=None):
        """crawl package info from mobbe, using package_name or package_id
        Keyword Arguments:
        package_name -- (default None)
        package_id   -- (default None)
        return -- crawled info dict
        """
        if package_name:
            self.package_name = package_name
            self.search_url = self.ios_search_url + package_name

        elif package_id:
            self.package_id = package_id
            self.package_name = None
            self.search_url = self.ios_search_url + package_id

        doc = self._request(self.search_url)
        res_list = doc('div.developerApps').children()

        result_list = []
        # mobbo not have it; using google search
        if not res_list and self.package_name is not None:
            result = {"_STATE": "GOOGLE"}
            g = Google("inurl:" + self.package_name)
            google_res = g.search()
            result['search_brief'] = google_res
            result['package_name'] = self.package_name
            result_list.append(result)

        # using mobbo result
        elif res_list:
            print("found %d res on mobbo" % len(res_list))
            for index, res in enumerate(res_list.items()):
                if index >= self.MAX_ITEM_NUM:
                    break
                print ("crawling No.%d res info" % index)
                result = {"_STATE": "MOBBO"}
                result['href'] = res('a').attr('href')
                result['package_name'] = self._get_package_name(result['href'])

                print ("crawling app name %s" % result['package_name'])

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
        else:
            result = {"_STATE": "NOT_FOUND"}
            result_list.append(result)

        return result_list

    def _get_package_name(self, href_str):
        return href_str.split('/')[-2]

    def _get_app_id(self, href_str):
        return href_str.split('/')[-1]


    def _get_scoring_num(self, string):

        return re.search("\d+", string).group(0)


    def _get_score(self, string):

        return re.search("\d+", string).group(0)


    def _parse_detail_page(self, detail_url):

        doc = self._request(detail_url)

        basic_info = {}
        basic_info['author_name'] = doc('div.info.clearfix')('a').eq(0).text()
        basic_info['main_cate'] = doc('div.info.clearfix')('a').eq(-2).text()
        basic_info['cate'] = doc('div.info.clearfix')('a').eq(-1).text()
        detail_info_generator = (item.text() for item in doc('div.newInnerDetails')('span').items())
        DetailInfo = namedtuple('DetailInfo', 'app_size, version, required_os, rating')
        detail_info = DetailInfo(*detail_info_generator)

        basic_info.update(detail_info._asdict())
        return basic_info


if __name__ == "__main__":
    ms = MobboSpider()
    ms.crawl()
    ms.crawl(package_name='cn.homoe.nicefoodbbtan')
    ms.crawl(package_id='1103632274')
