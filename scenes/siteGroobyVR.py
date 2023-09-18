import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGroobyVRSpider(BaseSceneScraper):
    name = 'GroobyVR'
    network = 'Grooby Network'
    parent = 'Grooby VR'
    site = 'Grooby VR'

    start_urls = [
        'https://www.groobyvr.com',
    ]

    selector_map = {
        'title': '//div[@class="in"]/following-sibling::text()',
        'description': '//div[@class="set_meta"]/following-sibling::p[1]/text()',
        'date': '//div[@class="set_meta"]/b[contains(text(), "Added")]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="trailer_toptitle_left"]/a/text()',
        'tags': '//div[@class="set_tags"]/ul/li/a/text()',
        'duration': '//div[@class="player-time"]/span/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="videoblock"]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        tags.append("VR")
        tags2 = []
        for tag in tags:
            tag = tag.replace("Shoot Type - ", "")
            tag = tag.replace("Other Features - ", "")
            if "Quality" in tag:
                tag = ""
            if "None" in tag:
                tag = ""
            if "View" in tag:
                tag = ""
            if "Hair" in tag:
                tag = ""
            if "Breasts" in tag:
                breasts = re.search(r' - (.*)', tag).group(1)
                tag = f"{breasts} Boobs"
            if tag:
                tags2.append(tag)

        return tags2
