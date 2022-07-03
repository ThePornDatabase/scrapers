import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSpermManiaSpider(BaseSceneScraper):
    name = 'SpermMania'
    network = 'SpermMania'
    parent = 'SpermMania'
    site = 'SpermMania'

    start_urls = [
        'https://www.spermmania.com/girls',
    ]

    limit_pages = 1

    selector_map = {
        'title': './/div[@class="scene-title"]//text()',
        'description': '',
        'date': './div[@class="scene-date"]//text()',
        'image': './div[@class="scene-img"]/@style',
        're_image': r'(http.*\.jpg)',
        'performers': '//div[contains(@class, "scene-array")]/h1/text()',
        'tags': './/div[@class="scene-type"]//text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/girls?page=%s'
    }

    def get_scenes(self, response):
        actresses = response.xpath('//div[@class="actress"]/a/@href').getall()
        for actress in actresses:
            yield scrapy.Request(url=self.format_link(response, actress), callback=self.parse_scene_from_model)

    def parse_scene_from_model(self, response):
        scenes = response.xpath('//div[@class="scene"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['tags'] = self.get_tags(scene)
            item['date'] = self.get_date(scene)
            item['description'] = ''
            item['image'] = self.get_image(scene)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(response)
            item['trailer'] = ''
            item['network'] = 'Sperm Mania'
            item['parent'] = 'Sperm Mania'
            item['site'] = 'Sperm Mania'
            item['id'] = re.search(r'preview/(.*?)/', item['image']).group(1)
            item['url'] = 'https://www.spermmania.com/videos/' + item['id']
            yield self.check_item(item, self.days)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            return image.replace(' ', '%20')
        return ''

    def get_title(self, response):
        if 'title' in self.get_selector_map():
            title = self.get_element(response, 'title', 're_title')
            if title:
                if isinstance(title, list):
                    title = " ".join(title)
                    title = title.replace("  ", " ").replace(" '", "'")
                return string.capwords(self.cleanup_text(title))
        return ''
