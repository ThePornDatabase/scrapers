#  Requires Splash for Image download (https://github.com/scrapinghub/splash)
#  Requires Flaresolverr for base page retrieval (https://github.com/FlareSolverr/FlareSolverr)
#  Please enter fields into settings.py with full command such as:
#  FLARE_ADDRESS = 'http://192.168.1.151:8191/v1'
#  SPLASH_ADDRESS = 'http://192.168.1.151:8050/run'

import re
from datetime import date, timedelta
import json
import base64
import requests
import scrapy
from scrapy.http import HtmlResponse
from scrapy.utils.project import get_project_settings

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJacquieEtMichelTVSpider(BaseSceneScraper):
    name = 'Jacquie'
    network = "Jacquie et Michel TV"
    parent = "Jacquie et Michel TV"

    cfcookies = {}

    settings = get_project_settings()
    flare_address = settings.get('FLARE_ADDRESS')
    splash_address = settings.get('SPLASH_ADDRESS')

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    start_urls = [
        'https://www.jacquieetmicheltv.net',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//span[@class="video-detail__date"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//span[@class="categories"]//a/text()',
        'external_id': r'/(\d+)/',
        'trailer': '',
        'pagination': '/en/videos/page%s.html'
    }

    def start_requests(self):
        if hasattr(self, 'start_page'):
            page = self.start_page
        else:
            page = self.page
        page = int(page)
        if page > 1:
            url = "https://www.jacquieetmicheltv.net/en/videos/page%s.html" % page
        else:
            url = "https://www.jacquieetmicheltv.net/en/"

        headers = self.headers
        headers['Content-Type'] = 'application/json'
        setup = json.dumps({'cmd': 'sessions.create', 'session': 'jacquie'})
        requests.post(self.flare_address, data=setup, headers=headers)
        my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'jacquie', 'cookies': [{'name': 'mypage', 'value': str(self.page)}]}
        yield scrapy.Request(self.flare_address, method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        self.cookies = cookies
        self.headers['User-Agent'] = jsondata['solution']['userAgent']
        for cookie in cookies:
            self.cfcookies[cookie['name']] = cookie['value']
            if cookie['name'] == 'mypage':
                page = int(cookie['value'])

        indexdata = {}
        indexdata['response'] = response
        indexdata['url'] = jsondata['solution']['url']
        scenes = self.get_scenes(indexdata)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count or page < 180:
            if page and page < self.limit_pages:
                page = page + 1
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = jsondata['solution']['url']
                url = self.get_next_page_url(url, page)
                print(f'Next Page URL: {url}')
                page = str(page)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'jacquie', 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request(self.flare_address, method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_scenes(self, indexdata):
        response = indexdata['response']
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        scenes = response.xpath('//div[@class="video-list" and not(./a/h2)]//a[@class="video-item__thumb"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'session': 'jacquie', 'url': "https://www.jacquieetmicheltv.net" + scene}
                yield scrapy.Request(self.flare_address, method='POST', callback=self.parse_scene, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                return list(map(lambda x: x.replace(",", "").strip().title(), tags.getall()))
        return []

    def get_performers(self, response):
        return []

    def get_site(self, response):
        return "Jacquie et Michel TV"

    def parse_scene(self, response):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        item = SceneItem()
        item['performers'] = []
        item['title'] = self.get_title(response)
        item['title'] = item['title'].replace(" ...", "")
        item['date'] = self.get_date(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob(response)
        item['tags'] = self.get_tags(response)
        if "" in item['tags']:
            item['tags'].remove("")
        item['id'] = re.search(r'\/(\d+)\/', jsondata['solution']['url']).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = jsondata['solution']['url']
        item['network'] = "Jacquie et Michel TV"
        item['parent'] = "Jacquie et Michel TV"
        item['site'] = "Jacquie et Michel TV"

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filterdate:
                item['filtered'] = "Scene filtered due to date restraint"
            print(item)
        else:
            if filterdate:
                if item['date'] > filterdate:
                    yield item
            else:
                yield item

    def get_image_blob(self, response):
        script = '''
            splash:set_viewport_size(806, 453)
            splash:go(args.url)
            return splash:png()
        '''
        image = self.get_image(response)
        if image:
            rsp = requests.post(self.splash_address, json={'lua_source': script, 'url': image})
            return base64.b64encode(rsp.content).decode('utf-8')
        return None

    def closed(self, response):
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        setup = json.dumps({'cmd': 'sessions.destroy', 'session': 'jacquie'})
        requests.post(self.flare_address, data=setup, headers=headers)
