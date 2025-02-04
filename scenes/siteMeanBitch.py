import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteMeanBitchSpider(BaseSceneScraper):
    name = 'MeanBitch'
    site = 'Mean Bitch'
    parent = 'Mean Bitch'
    network = 'Kink'

    start_urls = [
        'https://megasite.meanworld.com'
    ]

    selector_map = {
        'title': '//div[@class="update_block"]//span[@class="update_title"]/text()',
        'description': '//div[@class="update_block"]//span[@class="latest_update_description"]/text()',
        'date': '//div[@class="update_block"]//span[@class="availdate"]/text()[1]',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_table_right"]/div/a/img/@src0_3x|//div[@class="update_table_right"]/div/a/img/@src0_4x',
        'performers': '',
        'tags': '//div[@class="update_block"]//span[@class="update_tags"]/a/text()[1]',
        'trailer': '//div[@class="update_table_right"]/div[1]/a[1]/@onclick',
        're_trailer': r'[\'\"](.*?.mp4)[\'\"]',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            meta['performers'] = scene.xpath('.//span[@class="tour_update_models"]/a/text()').getall()
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_block"]//div[@class="update_counts_preview_table"]/text()').get()
        duration = duration.replace("&nbsp;", "").replace(" ", "").lower().strip()
        duration = re.search(r'(\d+)min', duration)
        if duration:
            duration = duration.group(1)
            return str(int(duration) * 60)
        return None
