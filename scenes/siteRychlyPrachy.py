import re
import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRychlyPrachySpider(BaseSceneScraper):
    name = 'RychlyPrachy'
    network = 'RychlyPrachy'
    parent = 'RychlyPrachy'
    site = 'RychlyPrachy'

    start_urls = [
        'https://rychlyprachy.cz',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "episode-details")]/text()',
        'description': '//div[contains(@class, "details__description")]/p/text()',
        'image': '//video/@poster',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="episode"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="date"]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%d.%m.%Y']).strftime('%Y-%m-%d')

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['European']

    def get_title(self, response):
        title = super().get_title(response)
        title = GoogleTranslator(source='cs', target='en').translate(title.lower())
        title = string.capwords(title)
        return title

    def get_description(self, response):
        description = super().get_description(response)
        description = GoogleTranslator(source='cs', target='en').translate(description.lower())
        description = string.capwords(description)
        return description
