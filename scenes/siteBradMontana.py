import re
import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'BradMontana'
    network = 'Brad Montana Studio'
    parent = 'Brad Montana Studio'
    site = 'Brad Montana Studio'

    start_urls = [
        'https://www.bradmontana.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "mx-auto flex w-full flex-col")]/div[contains(@class, "xl:text-lg")]/text()',
        'description': '//div[contains(@class, "mx-auto flex w-full flex-col")]/div[contains(@class, "leading-relaxed")]/p/text()',
        'date': '//script[@class="yoast-schema-graph"]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})T',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"models-slider-single")]//a/@title',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="flex flex-col gap-3 group"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Latina', 'Brazil', 'Spanish']

    def get_title(self, response):
        title = super().get_title(response).lower()
        if title:
            title = GoogleTranslator(source='pt', target='en').translate(title.lower())
            title = string.capwords(title)
        return title

    def get_description(self, response):
        description = super().get_description(response)
        if description:
            description = GoogleTranslator(source='pt', target='en').translate(description.strip())
            return description
        return ''
