import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClaraDeeSpider(BaseSceneScraper):
    name = 'ClaraDee'
    network = 'Clara Dee'
    parent = 'Clara Dee'
    site = 'Clara Dee'

    start_urls = [
        'https://claradeevids.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[@class="latest_update_description"]/text()',
        'date': '//span[@class="availdate"]/text()[contains(., "/")]',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//span[contains(@class, "update_tags")]/a/text()',
        'duration': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        return ['Clara Dee']

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]')
        if duration:
            duration = duration.get()
            if "min" in duration.lower():
                duration = duration.replace("&nbsp;", "")
                duration = re.search(r'(\d+)(?=[^\d]*min)', duration)
                if duration:
                    duration = str(int(duration.group(1)) * 60)
                return duration
        return None    
    
    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()