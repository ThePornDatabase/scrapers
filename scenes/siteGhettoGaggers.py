import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGhettoGaggersSpider(BaseSceneScraper):
    name = 'GhettoGaggers'
    network = 'D&E Media'
    parent = 'D&E Media'

    # Moved to DMEMediaV2
    start_urls = [
        # ~ 'https://tour5m.ghettogaggers.com',
        # ~ 'https://tour5m.ebonycumdumps.com'
    ]

    selector_map = {
        'title': '//h1[@class="highlight"]/text()',
        'description': '//div[contains(@class, "update-info-row")]/following-sibling::div[@class="update-info-block"][1]/text()',
        'date': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Added")]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'duration': '//div[contains(@class,"update-info-row")]/strong[contains(text(), "Added")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'image': '//img[contains(@id, "set-target")]/@src0_3x|//img[contains(@id, "set-target")]/@src0_2x|//img[contains(@id, "set-target")]/@src0_1x',
        'performers': '',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]/a/@href|//div[contains(@class,"item-thumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
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
        tags2 = []
        for tag in tags:
            if "movie" not in tag.lower() and "photos" not in tag.lower():
                tags2.append(tag)
        return tags2
