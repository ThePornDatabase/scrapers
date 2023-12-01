import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHousewifeKellySpider(BaseSceneScraper):
    name = 'HousewifeKelly'
    network = 'Housewife Kelly'
    parent = 'Housewife Kelly'
    site = 'Housewife Kelly'

    start_urls = [
        'https://www.housewifekelly.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]/span[@class="update_title"]/text()',
        'description': '//div[@class="update_block_info"]/span[@class="latest_update_description"]/text()',
        'date': '//div[@class="update_block_info"]/span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="update_image"]//img[contains(@class,"large_update_thumb left")]/@src',
        'performers': '',
        'tags': '//div[@class="update_block_info"]/span[@class="tour_update_tags"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour/updates/page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details" and contains(.//div[@class="update_counts"], "video")]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()

            scene = self.format_link(response, scene.xpath('./a[1]/@href').get())
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()').getall()
        duration = "".join(duration)
        duration = duration.replace("&nbsp;", "").strip().lower()
        duration = re.sub(r'[^a-z0-9]', '', duration)
        duration = re.search(r'(\d+)min', duration)
        if duration:
            duration = str(int(duration.group(1)) * 60)
            return duration
        return None

    def get_performers(self, response):
        return ['Kelly Anderson']

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace(".com/content", ".com/tour/content")
        return image
