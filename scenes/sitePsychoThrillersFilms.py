import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePsychoThrillersFilmsSpider(BaseSceneScraper):
    name = 'PsychoThrillersFilms'
    site = 'Psycho Thrillers Films'
    parent = 'Psycho Thrillers Films'
    network = 'Psycho Thrillers Films'

    start_urls = [
        'https://www.psycho-thrillersfilms.com'
    ]

    selector_map = {
        'title': '//h1/span/text()',
        'description': '//div[@itemprop="description"]/p[not(contains(text(), "Starring")) and not(contains(text(), "Size"))]/text()',
        'image': '//div[@data-gallery-role="gallery-placeholder"]/img/@src',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/shops.html?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="product-item-link"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@itemprop="description"]/p[contains(text(), "Starring")]/text()')
        if performers:
            performers = performers.get()
            performers = re.search(r'Starring:(.*) Time:', performers)
            if performers:
                performers = performers.group(1).strip()
                performers = performers.split(",")
                performers = list(map(lambda x: string.capwords(x.strip()), performers))
                return performers
        return None

    def get_duration(self, response):
        duration = response.xpath('//div[@itemprop="description"]/p[contains(text(), "Starring")]/text()')
        if duration:
            duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration.get())
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None
