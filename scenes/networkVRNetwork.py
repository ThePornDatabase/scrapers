import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class NetworkVRNetworkSpider(BaseSceneScraper):
    name = 'VRNetwork'
    network = 'VR Network'

    start_urls = [
        'https://vrbangers.com',
        'https://vrbgay.com',
        'https://vrbtrans.com',
        'https://vrconk.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class,"video-item__title")]/text()',
        'description': '//div[contains(@class,"second-text")]/div/p//text()',
        'date': '//div[contains(@class, "info-item") and contains(.//text(), "Release")]//text()',
        're_date': r'(\w{2,4} \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "info-item") and contains(.//text(), "Starring")]//a/text()',
        'tags': '//span[contains(@class, "position-title")]/text()',
        'trailer': '',
        'external_id': r'/video/(.*)/',
        'pagination': '/videos/?page=%s&sort=latest'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "video-item")]/a[contains(@href, "/video/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        scenedate = response.xpath(self.get_selector_map('date'))
        if scenedate:
            scenedate = scenedate.getall()
            scenedate = " ".join(scenedate)
            scenedate = re.search(self.get_selector_map('re_date'), scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
                return self.parse_date(self.cleanup_text(scenedate), date_formats=self.get_selector_map('date_formats')).isoformat()
        return self.parse_date('today').isoformat()

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("VR")
        return tags
