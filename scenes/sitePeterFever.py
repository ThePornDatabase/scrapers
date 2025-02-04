import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePeterFeverSpider(BaseSceneScraper):
    name = 'PeterFever'
    site = 'Peter Fever'
    parent = 'Peter Fever'
    network = 'Peter Fever'

    start_urls = [
        'https://www.peterfever.com',
    ]

    selector_map = {
        'description': '//h4/text()',
        'image': '//meta[@property="og:image"]/@content',
        'trailer': '//video//@src',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "product-item")]')
        for scene in scenes:
            title = scene.xpath('.//h3/a/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = self.parse_date(scenedate, date_formats=['%d %b %y']).strftime('%Y-%m-%d')

            scene = scene.xpath('.//h3/a/@href').get()

            meta['id'] = re.search(r'.*/(.*?)\.htm', scene).group(1).lower().replace("_vids", "")

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Asian', 'Gay']
