import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDesperatePleasuresXXXSpider(BaseSceneScraper):
    name = 'DesperatePleasuresXXX'
    site = 'Desperate Pleasures XXX'
    parent = 'Desperate Pleasures XXX'
    network = 'Desperate Pleasures XXX'

    start_urls = [
        'https://desperatepleasuresxxx.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="elementor-widget-container"]/p/text()',
        'date': '//span[contains(@class, "type-date")]/time/text()',
        'date_formats': ['%m/%d/%y'],
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@href, "category")]/text()',
        'trailer': '//video/@src',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/trailer/page/%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[contains(@class, "post-")]')
        for scene in scenes:
            sceneclass = scene.xpath('./@class').get()
            meta['id'] = re.search(r'post-(\d+)', sceneclass).group(1)

            performers = re.findall(r'model-name-([a-zA-Z-]+)', sceneclass)
            meta['performers'] = []
            for performer in performers:
                meta['performers'].append(string.capwords(performer.replace("-", " ")))

            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = response.meta['performers']
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Desperate Pleasures XXX"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = ""
        return image
