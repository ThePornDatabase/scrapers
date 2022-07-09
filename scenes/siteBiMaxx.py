import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBimaxxSpider(BaseSceneScraper):
    name = 'Bimaxx'
    network = 'Bimaxx'
    parent = 'Bimaxx'
    site = 'Bimaxx'

    start_urls = [
        'https://www.bimaxx.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[contains(@class, "info-wrap")]/p/text()',
        'date': '',
        'image': '//div[@class="header__film--img"]/picture//img/@src',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//figure/a[contains(@href, "login")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                sceneid = re.search(r'.*/(\d+)', scene).group(1)
                scene = f"https://www.bimaxx.com/tour/{sceneid}"
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        if "|" in title:
            title = re.search(r'(.*)\|', title).group(1)
        title = title.replace("...", "").replace(",", "").strip()
        return title

    def get_date(self, response):
        scenedates = response.xpath('//ul[contains(@class, "header__film")]/li/text()').getall()
        for scenedate in scenedates:
            if re.search(r'(\d{1,2} \w+ \d{4})', scenedate):
                scenedate = re.search(r'(\d{1,2} \w+ \d{4})', scenedate).group(1)
                return self.parse_date(scenedate, date_formats=['%d %b %Y']).isoformat()
        return self.parse_date('today').isoformat()
