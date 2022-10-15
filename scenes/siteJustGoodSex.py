import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJustGoodSexSpider(BaseSceneScraper):
    name = 'JustGoodSex'
    network = 'Just Good Sex'
    parent = 'Just Good Sex'
    site = 'Just Good Sex'

    start_urls = [
        'https://www.justgoodsex.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a/img/@src0_2x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '//div[@class="update_counts_preview_table"]/text()',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'(/.*\.mp4)',
        'external_id': r'updates/(.*)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            duration = re.search(r'(\d+).*?of video', duration.get())
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None
