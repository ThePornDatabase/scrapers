import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNikkiZeeXXXSpider(BaseSceneScraper):
    name = 'NikkiZeeXXX'
    network = 'nikkizee Studio'
    parent = 'nikkizee Studio'
    site = 'nikkizee Studio'

    start_urls = [
        'https://nikkizeexxx.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a[1]/img/@src0_1x',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub('[^a-zA-Z0-9]', '', duration)
            duration = duration.lower()
            if "minofvideo" in duration:
                duration = re.search(r'(\d+)minofvideo', duration)
                if duration:
                    duration = duration.group(1)
                    return str(int(duration) * 60)
        return None
