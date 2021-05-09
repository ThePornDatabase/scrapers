import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class InsexSpider(BaseSceneScraper):
    name = 'Insex'
    network = "Insex Network"
    parent = "Insex Network"

    start_urls = [
        'https://www.insexondemand.com'
    ]

    selector_map = {
        'title': '//div[contains(@class, "has-text-weight-bold")]/text()',
        'description': '//div[contains(@class, "has-text-white-ter")][3]/text()',
        'date': '//div[contains(@class, "has-text-white-ter")][1]//span[contains(@class, "is-dark")][1]/text()',
        'image': '//video-js[1]/@poster',
        'performers': '//div[contains(@class, "has-text-white-ter")][1]//a[contains(@class, "is-dark")][position() < last()]/text()',
        'tags': '',
        'external_id': 'play.php\\?id\\=(\\w+)',
        'trailer': '//video-js[1]//source/@src',
        'pagination': '/iod/home.php?p=%s&s=&d=&o=newest'
    }

    def get_scenes(self, response):
        scenes = response.css(
            "div.is-multiline div.column a::attr(href)").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, '/iod/' + scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath(
            '//div[contains(@class, "has-text-white-ter")][1]//a[contains(@class, "is-dark")][last()]/text()').get().strip()
        return site
