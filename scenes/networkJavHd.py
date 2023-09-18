import re
import json
import requests
import scrapy
from scrapy import Selector
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkJavHDSpider(BaseSceneScraper):
    name = 'JavHD'
    network = 'JavHD'
    parent = 'JavHD'
    site = 'JavHD'

    start_urls = [
        'https://javhd.com',
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    cookies = {
        'locale': 'en',
    }

    selector_map = {
        'title': '//h1[@class="content__title"]/text()',
        'description': '//h2[@class="content__desc"]/text()',
        'date': '',
        'image': '',
        'performers': '//strong[contains(text(), "Model")]/following-sibling::a/text()',
        'tags': '//div[@class="content-desc"]//a[contains(@href, "/category/") or contains(@href, "/tags/")]/span/text()',
        'external_id': r'id/(\d+)/',
        'trailer': '',
        'pagination': '/en/japanese-porn-videos/justadded/all/%s?content=all'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        # ~ print(jsondata)
        data = jsondata['template']
        data = data.replace("\n", "").replace("\t", "").replace("\r", "").replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        sel = Selector(text=data)
        scenes = sel.xpath('//thumb-component')

        for scene in scenes:
            meta['image'] = scene.xpath('./@url-thumb').get()
            meta['trailer'] = scene.xpath('./@video-preview').get()
            scene = scene.xpath('./@link-content').get()
            meta['id'] = None
            sceneid = re.search(r'id/(\d+)/', scene)
            if sceneid:
                meta['id'] = sceneid.group(1)

            if not meta['id']:
                sceneid = re.search(r'video/(\d+)$', scene)
                if sceneid:
                    meta['id'] = sceneid.group(1)

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, meta=meta)

    def get_image(self, response):
        externid = re.search(r'id/(\d+)/', response.url)
        if externid:
            externid = externid.group(1)
            payload = {'X-Requested-With': 'XMLHttpRequest', 'Cookie': 'locale=en'}
            headers = {}
            url = "https://javhd.com/en/player/" + externid.strip() + "?is_trailer=1"
            if externid:
                image = requests.post(url, data=json.dumps(payload), headers=headers)
                jsondata = image.json()
                image = jsondata['poster'].strip()
                return image
            return ''
        else:
            image = re.search(r'poster\:.*?[\'\"](http.*?)[\'\"]', response.text)
            if image:
                image = image.group(1)
                return image
            return ''

    def get_trailer(self, response):
        externid = re.search(r'id/(\d+)/', response.url)
        trailer = None
        if externid:
            externid = externid.group(1)
            payload = {'X-Requested-With': 'XMLHttpRequest', 'Cookie': 'locale=en'}
            headers = {}
            url = "https://javhd.com/en/player/" + externid.strip() + "?is_trailer=1"
            if externid:
                trailer = requests.post(url, data=json.dumps(payload), headers=headers)
                jsondata = trailer.json()
                trailer = jsondata['sources'][0]['src'].strip()
        else:
            trailer = re.search(r'poster\:.*?[\'\"](http.*?)[\'\"]', response.text)
            if trailer:
                trailer = trailer.group(1)

        if trailer and "mp4" in trailer:
            return trailer
        return None

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("\r\n", " ")
        return description
