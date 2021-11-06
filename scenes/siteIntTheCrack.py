# This scraper is a mess, admittedly.  Unfortunately not much documenation
# on Flaresolverr, or examples for Python/Scrapy, so I had to work with
# what I could figure out.  And please don't hack my systems because you
# know my IP is 192.168.1.151.  <snicker>
# But if you set up Flaresolverr, just replace that IP

import os
import re
import json
import datetime
import dateparser
import requests
import scrapy
from scrapy.http import HtmlResponse

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class InTheCrackSpider(BaseSceneScraper):
    name = 'InTheCrack'
    network = 'In The Crack'
    parent = 'In The Crack'

    start_urls = [
        'https://inthecrack.com/',
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1
    }

    selector_map = {
        'title': '//section[@class="modelCollectionHeader"]/h2/span/text()',
        'description': '//div[@class="ClipDetail"]//p/text()',
        'date': '',
        'image': '//style[contains(text(),"background-image")]/text()',
        'performers': '//section[@class="modelCollectionHeader"]/h2/span/text()',
        'tags': '',
        'external_id': r'/(\d*)$',
        'trailer': '',  # Videos listed in code require login
        'pagination': '/Collections/Date/%s'
    }

    def start_requests(self):
        for link in self.start_urls:
            url = self.get_next_page_url(link, self.page)
            headers = self.headers
            headers['Content-Type'] = 'application/json'
            setup = json.dumps({'cmd': 'sessions.create', 'session': 'inthecrack'})
            requests.post("http://192.168.1.151:8191/v1", data=setup, headers=headers)
            my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'inthecrack', 'cookies': [{'name': 'mypage', 'value': str(self.page)}]}
            yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        for cookie in cookies:
            if cookie['name'] == 'mypage':
                page = int(cookie['value'])
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if page and page < self.limit_pages:
                page = page + 1
                print('NEXT PAGE: ' + str(page))
                headers = self.headers
                headers['Content-Type'] = 'application/json'
                url = self.get_next_page_url("https://inthecrack.com", page)
                page = str(page)
                my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'inthecrack', 'cookies': [{'name': 'mypage', 'value': page}]}
                yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        year = datetime.datetime.now().year + 1
        year = str(year - page)
        url = self.format_url(
            base, self.get_selector_map('pagination') % year)
        return url

    def get_scenes(self, response):
        headers = self.headers
        headers['Content-Type'] = 'application/json'
        scenes = response.xpath('//ul[@class="collectionGridLayout"]/li/a[contains(@href,"Collection")]')
        for scene in scenes:
            scenedate = scene.xpath('./span[2]/text()').get()
            if scenedate:
                date = scenedate.strip()
            else:
                date = dateparser.parse('today').isoformat()
            scene = scene.xpath('./@href').get()
            url = "https://inthecrack.com" + scene
            my_data = {'cmd': 'request.get', 'maxTimeout': 60000, 'url': url, 'session': 'inthecrack', 'cookies': [{'name': 'mydate', 'value': date}]}
            yield scrapy.Request("http://192.168.1.151:8191/v1", method='POST', callback=self.parse_scene, body=json.dumps(my_data), headers=headers, cookies=self.cookies)

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return title.replace("  ", " ").strip()
        return ''

    def get_description(self, response):
        description = ''
        desc_sections = response.xpath('//div[@class="ClipDetail"]')
        if desc_sections:
            for desc_section in desc_sections:
                desc_title = desc_section.xpath('./div/h4/text()').get()
                desc_description = desc_section.xpath('./div/p/text()').get()
                if desc_title and desc_description:
                    description = description + desc_title.strip() + os.linesep + desc_description + os.linesep
                    description = description.replace("\r\n", "\n")

        return description

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if "url" in image:
            image = re.search(r'url\(\'(.*)\'\)', image).group(1)
            if image:
                image = 'https://www.inthecrack.com' + image.strip()
            else:
                image = ''

        if image:
            return self.format_link(response, image)
        return ''

    def get_performers(self, response):
        performers = []
        performer_text = self.process_xpath(
            response, self.get_selector_map('performers')).get()
        if performer_text:
            performer_text = re.search(r'^\d+\s+?(.*)', performer_text).group(1)
            if performer_text:
                performers = performer_text.strip().split("&")

        if performers:
            return list(map(lambda x: x.strip(), performers))
        return []

    def parse_scene(self, response):
        jsondata = response.json()
        htmlcode = jsondata['solution']['response']
        response = HtmlResponse(url=response.url, body=htmlcode, encoding='utf-8')
        cookies = jsondata['solution']['cookies']
        for cookie in cookies:
            if cookie['name'] == 'mydate':
                date = cookie['value']

        item = SceneItem()
        if date:
            item['date'] = dateparser.parse(date).isoformat()
        else:
            item['date'] = dateparser.parse('today').isoformat()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = re.search(r'(\d+) ', item['title']).group(1)
        item['trailer'] = self.get_trailer(response)
        item['url'] = jsondata['solution']['url']
        item['network'] = "In The Crack"
        item['parent'] = "In The Crack"
        item['site'] = "In The Crack"

        if self.debug:
            print(item)
        else:
            yield item
