import re
import requests
import scrapy
import urllib.parse
from tpdb.helpers.http import Http
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDreddXXXSpider(BaseSceneScraper):
    name = 'DreddXXX'
    network = 'DreddXXX'
    parent = 'DreddXXX'
    site = 'DreddXXX'

    start_urls = [
        'https://officialdreddxxx.com/',
    ]

    cookies = [{"name": "age_gate", "value": "44"}]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'date': '//time[contains(text(), ",")]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "terms-list")]/a[contains(@href, "pornstar")]/text()',
        'tags': '//span[contains(@class, "terms-list")]/a[contains(@href, "category")]/text()',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': 'https://officialdreddxxx.com/%s',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(text(), "New Releases")]/ancestor::div[contains(@class, "e-con-full")][1]/following-sibling::div[contains(@class, "e-con-boxed")][1]//article/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        protocol, _, rest_of_url = image.partition("://")
        encoded_rest = urllib.parse.quote(rest_of_url, safe="/:")
        return f"{protocol}://{encoded_rest}"



    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None
