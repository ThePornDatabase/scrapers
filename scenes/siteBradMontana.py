import re
import string
import scrapy
from googletrans import Translator
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
        'title': '//div[@class="title"]/h1/text()',
        'description': '//div[@class="descript"]/p/text()',
        'date': '//script[@class="yoast-schema-graph"]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})T',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="elenco"]/a/text()',
        'tags': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/videos/page/%s/?theme=active'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[@class="post"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Latina', 'Brazil', 'Spanish']

    def get_title(self, response):
        translator = Translator()
        title = super().get_title(response).lower()
        if title:
            title = translator.translate((title.lower()), src='pt', dest='en')
            title = string.capwords(title.text)
        return title

    def get_description(self, response):
        translator = Translator()
        description = super().get_description(response)
        if description:
            description = translator.translate((description.strip()), src='pt', dest='en')
            description = description.text.strip()
            return description
        return ''
