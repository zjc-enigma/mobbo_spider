#coding=utf-8
import os
from os.path import isfile, join
import sys
import urllib, socket, time
import gzip
from io import StringIO, BytesIO
import re, random, types
import requests
import json
from lxml import etree
sys.path.append('..')
from bs4 import BeautifulSoup
import pdb

def get_user_agent():
    headers = "Mozilla/5.0 (compatible; Scrubby/2.1; +http://www.scrubtheweb.com/abs/meta-check.html)"
    return headers



class SearchToutiao(object):

    def __init__(self, keywords, count=20, offset=0, search_limit=20):
        self.keywords = keywords
        self.count = count
        self.offset = offset
        self.search_limit = search_limit
        self.search_res_list = []
        self.search_doc_list = []
        self.search_url_list = []
        self.search_image_list = []

    def search_keyword(self):
        base_api = "http://toutiao.com/search_content/?offset={offset}&format=json&keyword={keywords}&autoload=true&count={count}"

        api_url = base_api.format(offset=self.offset,
                                  keywords=self.keywords,
                                  count=self.count)
        headers = {'User-Agent':get_user_agent()}
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        ret_html = ""
        res_list = []

        try:
            ret = requests.get(api_url, headers=headers)
            ret_html = ret.text
            ret_json = json.loads(ret_html)
            res_list = ret_json['data']

            while ret_json["has_more"] == 1 and len(res_list) < self.search_limit:
                self.offset += self.count
                api_url = base_api.format(offset=self.offset,
                                          keywords=self.keywords,
                                          count=self.count)
                ret = requests.get(api_url, headers=headers)
                ret_html = ret.text
                ret_json = json.loads(ret_html)
                res_list += ret_json['data']

        except ValueError as ve:
            print ("html return %s" % ret_html)

        except Exception as e:
            print ("html return %s" % ret_html)
            print ("exception type: %s" %  type(e))
            print ("exception during search : %s ") % str(e)

        return res_list

    def get_search_res(self):
        res_list = self.search_keyword()

        for item in res_list:
            title = item['title']
            url = item['url']
            #media_name = item['media_name']
            abstract = item['abstract']
            keywords = item['keywords']
            image_list = item['image_list']
            #media_url = item['media_url']
            article_url = item['article_url']
            display_url = item['display_url']

            self.search_res_list.append({"title": title,
                                         "url": url})
            doc = title + " " + abstract + " " + keywords
            self.search_doc_list.append(doc)
            self.search_url_list.append(url)
            self.search_image_list.append(image_list)

        return self.search_res_list,self.search_doc_list,self.search_url_list,self.search_image_list


class Google:
    # search web
    # @param query -> query key words
    # @param lang -> language of search results
    # @param num -> number of search results to return
    # 192.210.165.110:80:92316cheng:gproxy2

    def __init__(self, query, lang='zh', num=30):
        #timeout = 40
        #socket.setdefaulttimeout(timeout)
        self.query = query
        self.lang = lang
        self.num = num
        self.results_per_page = 10
        self.base_url = 'https://www.google.com.hk/'
        self.search_doc_list = []
        self.search_url_list = []
        self._set_proxy()

    def _set_proxy(self):
        proxy_ip_list = ["158.222.4.237",
                         "158.222.4.207",
                         "192.210.165.101",
                         "104.203.43.36",
                         "107.173.254.211"]
        proxy_server = random.choice(proxy_ip_list)
        print("using proxy ip", proxy_server)
        #proxy_server = "158.222.4.237"
        proxy_port = 80
        proxy_user = "92316cheng"
        proxy_passwd = "gproxy2"
        proxy_support = urllib.request.ProxyHandler({
            "http": "http://{user}:{passwd}@{server}:{port}".format(user=proxy_user,
                                                                    passwd=proxy_passwd,
                                                                    server=proxy_server,
                                                                    port=proxy_port),

            "https": "https://{user}:{passwd}@{server}:{port}".format(user=proxy_user,
                                                                    passwd=proxy_passwd,
                                                                    server=proxy_server,
                                                                    port=proxy_port),
        })
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)


    def _test_proxy(self):
        rq = urllib.request.Request('http://www.google.com')
        #rq.set_proxy(proxy_host, 'http')
        res = urllib.request.urlopen(rq)
        print(res.read())


    def randomSleep(self):
        sleeptime =  random.randint(60, 120)
        time.sleep(sleeptime)

    #extract the domain of a url
    def extractDomain(self, url):
        domain = ''
        pattern = re.compile(r'http[s]?://([^/]+)/', re.U | re.M)
        url_match = pattern.search(url)
        if(url_match and url_match.lastindex > 0):
            domain = url_match.group(1)

        return domain

    #extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]+)&', re.U | re.M)
        url_match = pattern.search(href)
        if(url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url

    # extract serach results list from downloaded html file
    def extractSearchResults(self, html):
        url_list, doc_list = [], []
        soup = BeautifulSoup(html, 'lxml')
        div = soup.find('div', id  = 'search')
        if (type(div) != type(None)):
            lis = div.findAll('div', {'class': 'g'})
            if(len(lis) > 0):
                for li in lis:
                    h3 = li.find('h3', {'class': 'r'})
                    if(type(h3) == type(None)):
                        continue
                    # extract domain and title from h3 object
                    link = li.find('a')
                    if (type(link) == type(None)):
                        continue

                    url = link['href']
                    url = self.extractUrl(url)
                    # if(cmp(url, '') == 0):
                    #     continue
                    if url.strip() == '':
                        continue

                    title = link.renderContents().decode('utf8')
                    content = li.text

                    self.search_url_list.append(url)

                    doc = title + " " + content
                    self.search_doc_list.append(doc)

    def search(self):
        query = urllib.parse.quote(self.query)
        results_per_page = self.results_per_page
        num = self.num
        base_url = self.base_url
        if(num % results_per_page == 0):
            pages = int(num / results_per_page)
        else:
            pages = int(num / results_per_page + 1)

        for p in range(0, pages):
            start = p * results_per_page
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, self.lang, results_per_page, start, query)
            retry = 3
            while(retry > 0):
                try:
                    request = urllib.request.Request(url)
                    user_agent = get_user_agent()
                    request.add_header('User-agent', user_agent)
                    request.add_header('connection','keep-alive')
                    request.add_header('Accept-Encoding', 'gzip')
                    request.add_header('referer', base_url)
                    response = urllib.request.urlopen(request)
                    html = response.read()
                    if(response.headers.get('content-encoding', None) == 'gzip'):
                        html = gzip.GzipFile(fileobj=BytesIO(html)).read()

                    self.extractSearchResults(html)
                    break

                except urllib.error.URLError as e:
                    print('url error:', e)
                    self.randomSleep()
                    self._set_proxy()
                    retry = retry - 1
                    continue

                except Exception as e:
                    retry = retry - 1
                    self.randomSleep()
                    continue

        #return self.search_url_list, self.search_doc_list
        return "|".join(self.search_doc_list[:3])


class Baidu:
    # search web
    # @param query -> query key words
    def __init__(self, query):
        timeout = 10
        self.query = query
        self.search_doc = ""

    def download_html(self, keywords):
        key = {'wd': keywords}
        headers = {'User-Agent': get_user_agent()}
        web_content = requests.get("http://www.baidu.com/s?", params=key, headers=headers, timeout=10)
        content = web_content.text
        return content

    def html_parser(self, html):
        path = "//div[@id='content_left']//div[@class='c-abstract']/text()"  # Xpath of abstract in BaiDu search results
        tree = etree.HTML(html)
        results = tree.xpath(path)
        text = [line.strip() for line in results]
        text_str = ''
        if len(text) == 0:
            print("No!")
        else:
            for i in text:
                i = i.strip()
                text_str += i
        text_str = text_str.replace('\n', ' ').replace('\t', ' ')
        return text_str

    def search(self):
        html = self.download_html(self.query)
        self.search_doc = self.html_parser(html)

def main_Baidu(keyword='中兴', fkey='test'):
    bd = Baidu(keyword)
    bd.search()
    return bd.search_doc    
    
def main_TD(keyword='中兴', fkey='test'):
    st = SearchToutiao(keyword)
    res_list, doc_list, url_list, image_list = st.get_search_res()

    outfile = "../data/doc_" + fkey
    fwd = open(outfile, 'w')
    fwd.write(" ".join(doc_list))

    #outfile = "../data/img_" + fkey
    #fwd = open(outfile, 'w')
    #fwd.write(" ".join(image_list))
    print(" ".join(image_list))

def main_GG(keyword='方太', fkey='test'):
    gs = Google(keyword)    
    url_list, doc_list = gs.search()

    outfile = "../data/doc_" + fkey
    if os.path.exists(outfile):
        os.remove(outfile)
    fwd = open(outfile, 'a')
    fwd.write(" ".join(doc_list))

if __name__ == "__main__":
    #main_GG()
    #main_TD()
    main_Baidu()

