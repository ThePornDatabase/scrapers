import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCockyBoysSpider(BaseSceneScraper):
    name = 'CockyBoys'
    network = 'Cocky Boys'
    parent = 'Cocky Boys'
    site = 'Cocky Boys'

    start_urls = [
        'https://cockyboys.com',
    ]

    selector_map = {
        'title': '//div[@id="movieHeader"]//h1/text()',
        'description': '//div[@class="movieDesc"]//text()',
        'date': '//strong[contains(text(), "eleased:")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'performers': '//strong[contains(text(), "eaturing:")]/following-sibling::a/text()',
        'tags': '//strong[contains(text(), "ategorized")]/following-sibling::a/text()',
        'trailer': '//script[contains(text(), df_movie)]/text()',
        're_trailer': r'df_movie.*?(http.*?)[\'\"]',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//section[contains(@class,"previewThumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id')
            if sceneid:
                meta['id'] = sceneid.get()
            image = scene.xpath('.//video/@poster')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            duration = scene.xpath('.//em[contains(text(), "inutes")]/text()')
            if duration:
                duration = duration.get()
                if re.search(r'(\d+) [mM]in', duration):
                    meta['duration'] = str(int(re.search(r'(\d+) [mM]in', duration).group(1)) * 60)
            scene = scene.xpath('./a[contains(@href, "/scenes/")]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("Description", "").strip()
        return description
