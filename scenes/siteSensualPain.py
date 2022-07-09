import re
import base64
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSensualPainSpider(BaseSceneScraper):
    name = 'SensualPain'
    network = 'Sensual Pain'
    parent = 'Sensual Pain'
    site = 'Sensual Pain'

    start_urls = [
        'https://sensualpain.com',
    ]

    selector_map = {
        'title': '//div[@class="grid-container"]/div[@class="item2"]/font/b/text()',
        're_title': r'(.*) - ',
        'description': '//div[@class="grid-container"]/div[@class="item2"]/font/following-sibling::text()[1]',
        'date': '',
        'image': '//img[@alt="Main Image"]/@src',
        'performers': '',
        'tags': '//div[@class="grid-container"]/div[@class="item2"]/font/following-sibling::a[contains(@href, "Fetish")]/u/b/text()',
        'external_id': r'ID=(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/Videos.php?Media=ALL&Page=%s'
    }

    def get_scenes(self, response):
        cookies = response.headers.getlist("Set-Cookie")
        scenes = response.xpath('//div[@class="galleryEntry"]/ul/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'mycookies': cookies})

    def get_title(self, response):
        title = super().get_title(response)
        if " - " in title:
            title = re.search(r'(.*?) - ', title).group(1)
        return title

    def get_image_blob(self, response):
        image = super().get_image(response)
        if image:
            phpsessid = re.search(r'PHPSESSID=(.*?);', str(response.meta['mycookies']))
            if phpsessid:
                cookies_dict = {'PHPSESSID': phpsessid.group(1)}
            else:
                cookies_dict = ''

            header_dict = {'Referer': 'https://sensualpain.com'}
            if image:
                return base64.b64encode(requests.get(image, headers=header_dict, cookies=cookies_dict).content).decode('utf-8')
        return None
