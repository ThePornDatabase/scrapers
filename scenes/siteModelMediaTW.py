import re
import string
import scrapy
# ~ from googletrans import Translator
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteModelMediaAsiaSpider(BaseSceneScraper):
    name = 'ModelMediaAsia'
    network = 'Model Media'
    parent = 'Model Media'
    site = 'Model Media Asia'

    start_urls = [
        'https://www.modelmediaasia.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//h3//following-sibling::p/text()',
        'date': '//td[contains(text(), "Released")]/following-sibling::td/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '//td[contains(text(), "Cast")]/following-sibling::td/a/text()',
        'tags': '//td[contains(text(), "Tags")]/following-sibling::td/a/text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/videos?sort=published_at&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "video-preview-media")]/a')
        for scene in scenes:
            image = scene.xpath('./div/img/@src')
            if image:
                image = self.format_link(response, image.get())
            else:
                image = ''
            trailer = scene.xpath('.//video/@data-src')
            if trailer:
                trailer = self.format_link(response, trailer.get())
            else:
                trailer = ''
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image, 'trailer': trailer})

    def get_title(self, response):
        title = super().get_title(response).lower()
        if title:
            title = GoogleTranslator(source='auto', target='en').translate(title.lower())
            title = string.capwords(title)
        return title

    def get_description(self, response):
        description = super().get_description(response).lower()
        if description:
            try:
                description = GoogleTranslator(source='auto', target='en').translate(description.lower())
                description = string.capwords(description)
            except Exception:
                description = string.capwords(description)
        return description

    def get_performers(self, response):
        performers = super().get_performers(response)
        try:
            performers = list(map(lambda x: string.capwords(GoogleTranslator(source='auto', target='en').translate(x.lower())), performers))
        except Exception:
            performers = list(map(lambda x: x.strip(), performers))
        performerlist = []
        for performer in performers:
            if "/" in performer:
                performerbreak = re.search(r'/(.*)', performer)
                if performerbreak:
                    performer = performerbreak.group(1)
            performerlist.append(string.capwords(performer.strip()))

        return performerlist
