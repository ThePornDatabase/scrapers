import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEmilyBloomSpider(BaseSceneScraper):
    name = 'EmilyBloom'
    network = 'Emily Bloom'
    parent = 'Emily Bloom'
    site = 'Emily Bloom'

    start_urls = [
        'https://emilybloom.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]//text()',
        'date': '//span[@class="availdate"]//text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"update_counts")]//text()[contains(., "video")]')
        if duration:
            duration = duration.get()
            duration = duration.replace("&nbsp;", "")
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
    
    def get_id(self, response):
        external_id = re.search(self.get_selector_map('external_id'), response.url)
        if external_id:
            return external_id.group(1).lower()
        return None
    
    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer_data = {}
            performer_data['name'] = performer.strip()
            performer_data['url'] = f"https://emilybloom.com/models/{performer_data['name'].lower().replace(' ', '')}.html"
            performer_data['site'] = "Emily Bloom"
            performer_data['extra'] = {}
            performer_data['extra']['gender'] = "Female"
            performers_data.append(performer_data)
        return performers_data