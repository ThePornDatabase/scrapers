import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJawkedSpider(BaseSceneScraper):
    name = 'Jawked'
    site = 'Jawked'
    parent = 'Jawked'
    network = 'Jawked'

    cookies = {"warningHidden": "hide"}

    start_urls = [
        'https://www.jawked.com'
    ]

    selector_map = {
        'title': '//span[@class="title"]/text()',
        'description': '//div[@class="heading"]/following-sibling::p/text()',
        'date': '//span[@class="heading" and contains(text(), "Added")]/following-sibling::span/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//span[@class="heading" and contains(text(), "Starring")]/following-sibling::span/a/text()',
        'trailer': '//video/source/@src',
        'type': 'Scene',
        'external_id': r'-(\d+)',
        'pagination': '/videos/page%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item"]/div[1]/a')
        for scene in scenes:
            image = scene.xpath('.//img/@data-src').get()
            if image:
                meta['orig_image'] = image

            scene = scene.xpath('./@href').get()
            if "video" in scene:
                if re.search(self.get_selector_map('external_id'), scene):
                    url=self.format_link(response, scene)
                    yield scrapy.Request(url, callback=self.parse_scene, meta=meta, cookies=self.cookies)

    def get_tags(self, response):
        return ['Gay']

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Jawked"
                perf['site'] = "Jawked"
                performers_data.append(perf)
        return performers_data

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.meta['orig_image']
        return image
