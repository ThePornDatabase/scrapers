import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePAWGNextDoorSpider(BaseSceneScraper):
    name = 'PAWGNextDoor'
    network = 'PAWG Next Door'
    parent = 'PAWG Next Door'
    site = 'PAWG Next Door'

    start_urls = [
        'https://www.pawgnextdoor.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]/span[contains(@class, "update_title")]/text()',
        'description': '//div[@class="update_block_info"]/span[contains(@class, "update_description")]/text()',
        'date': '//div[@class="update_block_info"]/span[contains(@class, "availdate")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content|//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="update_block_info"]/span[contains(@class, "update_models")]/a/text()',
        'tags': '//div[@class="update_block_info"]/span[contains(@class, "update_tags")]/a/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "")
            duration = re.search(r'(\d+).*?min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None

    def get_trailer(self, response):
        trailer = response.xpath('//div[@class="update_image"]/a[1]/@onclick')
        if trailer:
            trailer = re.search(r'\'(.*)\'', trailer.get())
            if trailer:
                trailer = 'https://www.pawgnextdoor.com/tour/' + trailer.group(1)
                return trailer
        return None
