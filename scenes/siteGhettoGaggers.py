import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGhettoGaggersSpider(BaseSceneScraper):
    name = 'GhettoGaggers'
    network = 'D&E Media'
    parent = 'D&E Media'

    start_urls = [
        'https://tour5m.ghettogaggers.com',
        'https://tour5m.ebonycumdumps.com'
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '',
        'image': '//img[contains(@src, "full.jpg")]/@src',
        're_image': r'poster=\"(http.*?)\"',
        'performers': '',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                scene = f"/tour/{scene}"
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = response.xpath('//img[contains(@src, "full.jpg")]/@src')
        if image:
            image = image.get()
        if "jpg" not in image:
            image = response.xpath('//script[contains(text(), "poster")]/text()')
            if image:
                image = re.search(r'poster=\"(http.*?)\"', image.get()).group(1)
        return image

    def get_site(self, response):
        if "ghettogaggers" in response.url:
            return "Ghetto Gaggers"
        if "ebonycum" in response.url:
            return "Ebony Cum Dumps"

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "ebonycumdumps" in response.url:
            tags = []
        return tags

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts"]/b[contains(text(), "Runtime")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(", (\d+)", duration)
            if duration:
                duration = (int(duration.group(1)) * 60)
        return duration
