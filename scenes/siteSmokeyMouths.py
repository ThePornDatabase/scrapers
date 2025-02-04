import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSmokeyMouthsSpider(BaseSceneScraper):
    name = 'SmokeyMouths'
    site = 'Smokey Mouths'
    parent = 'Smokey Mouths'
    network = 'Smokey Mouths'

    start_urls = [
        'https://smokeymouths.com'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img[not(contains(@src, "play.png"))]/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/tour/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Smoking']

    def get_duration(Self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace("&nbsp;", "").strip()
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
