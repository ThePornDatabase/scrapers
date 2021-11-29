import re
import html
from unidecode import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLaFranceAPoilSpider(BaseSceneScraper):
    name = 'LaFranceAPoil'
    network = 'La France a Poil'
    parent = 'La France a Poil'
    site = 'La France a Poil'

    start_urls = [
        'https://www.lafranceapoil.com',
    ]

    cookies = {
        'disclaimerlfap': 'oui',
    }

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//p[contains(text(), "Added :")]/text()',
        're_date': r'Added : (.*?)\s*-',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//p[contains(text(), "Starring")]/a/text()',
        'tags': '//p[contains(text(), "Tags")]/a/text()',
        'external_id': r'video=(\d+)',
        'trailer': '',
        'pagination': '/portal/more.php?aff=&page=%s&tag=&amatrice=&cat=&video=&search=&thid=&tr=&trlfap=&cp=&tunl=&iduser=&catalogue=&serie=&lang=en'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href,"/video?")]/@href').getall()
        for scene in scenes:
            scene = html.unescape(scene)
            scene = scene.replace("\\", " ").replace("\"", "").replace(" ", "")
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
            else:
                print(f'Didnt pull scene: {scene}')

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if tags:
            tags.append("European")
        return tags

    def get_title(self, response):
        title = super().get_title(response)
        title = unidecode(title)
        return self.cleanup_title(title)

    def get_description(self, response):
        description = super().get_description(response)
        description = unidecode(description)
        return self.cleanup_description(description)
