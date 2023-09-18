import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXevUnleashedSpider(BaseSceneScraper):
    name = 'XevUnleashed'
    network = 'XevUnleashed'
    parent = 'XevUnleashed'
    site = 'XevUnleashed'

    start_urls = [
        'https://xevunleashed.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()[1]',
        'date': '//span[@class="availdate"]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]/a[2]/img/@src',
        'performers': '',
        'tags': '//span[@class="update_tags"]/a/text()[1]',
        'duration': '',
        'trailer': '//div[@class="update_image"]/a[1]/@onclick',
        're_trailer': r'\'(.*)\'',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "updateItem")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Xev Bellringer']

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()')
        if duration:
            duration = duration.get()
            if "of video" in duration:
                duration = re.search(r'(\d+).{2,7}of\ video', duration)
                if duration:
                    duration = duration.group(1)
                    return str(int(duration) * 60)
        return None
