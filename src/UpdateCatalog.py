#
# California compensation by city. Files are updated every working
# weekday
#
# Copyright (c) <2017> <Larz60+>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Credits:
#     Thanks to Snippsat for showing me how to scrape ASP.NET page.
#
# Author Larz60+
#
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
import os
import json


class UpdateCatalog:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.ca_comp = {
            'url_dict': {},
            'data_dict': {}
        }

    def set_nested(self, dict, value, *path):
        for level in path[:-1]:
            dict = dict.setdefault(level, {})
        dict[path[-1]] = value

    def fetch_urls(self, url, class_name=None):
        gotdatadict = False
        urlsplit = urlparse(url)
        baseurl = '{}://{}'.format(urlsplit.scheme, urlsplit.netloc)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')
        col = soup.find('div', class_=class_name)
        col_all = col.find_all('a')
        for link in col_all:
            if str(link).startswith('Data'):
                break
            fullpath = '{}{}'.format(baseurl, link.get('href'))
            linksplit = urlparse(fullpath)
            basename = os.path.basename(linksplit.path)
            if not basename.startswith('DataDictionary'):
                year = basename[0:4]
                name = basename[5:-4]
            else:
                if gotdatadict:
                    break
                gotdatadict = True
                year = 0
                name = basename[:-5]
            self.set_nested(self.ca_comp['url_dict'], fullpath, name, year)

    def fetch_datadict(self, url, class_name=None):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'lxml')

        col = soup.find("table", {"class": class_name})
        firstrow = True
        for row in col.findAll('tr'):
            if firstrow:
                firstrow = False
                continue
            all_td = row.findAll('td')
            self.ca_comp['data_dict'][all_td[1].string.strip()] = all_td[2].string.strip()

    def build_json_data(self, url):
        self.fetch_urls(url=url, class_name='column_main')
        self.fetch_urls(url=url, class_name='column_right')

        durl = self.ca_comp['url_dict']['DataDictionary'][0]
        self.fetch_datadict(url=durl, class_name='data_table striped')

        # display results
        if self.verbose:
            print('\nurl_dict:')
            for key, value in self.ca_comp['url_dict'].items():
                print('key: {}, value: {}'.format(key, value))
            print('\ndata_dict:')
            for key, value in self.ca_comp['data_dict'].items():
                print('key: {}, value: {}'.format(key, value))
        if not os.path.isdir('data'):
            os.mkdir('data')
        with open('data/CaCityCompensation.json', 'w') as f:
            json.dump(self.ca_comp, f)


if __name__ == '__main__':
    catalog_url = 'http://publicpay.ca.gov/Reports/RawExport.aspx'
    gcgc = UpdateCatalog(verbose=True)
    gcgc.build_json_data(catalog_url)

