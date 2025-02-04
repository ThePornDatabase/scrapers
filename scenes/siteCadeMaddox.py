import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCadeMaddoxSpider(BaseSceneScraper):
    name = 'CadeMaddox'
    network = 'CadeMaddox'
    parent = 'CadeMaddox'
    site = 'CadeMaddox'

    start_urls = [
        'https://cademaddox.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//p[contains(@class, "update_description")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '',
        'trailer': '//source[contains(@type, "video")]/@src',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateDetails"]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[@class="details"]/span[@class="availdate"][1]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            duration = scene.xpath('.//div[@class="details"]/span[@class="availdate"][2]/text()')
            if duration:
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration.get())
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']
