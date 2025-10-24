import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXArtSpider(BaseSceneScraper):
    name = 'X-Art'
    network = "BC Media"
    parent = "X-Art"

    start_urls = [
        'https://www.x-art.com',
    ]

    selector_map = {
        'title': '//div[@class="info"]/div/h1/text()',
        'description': '//div[contains(@class,"info")]/p//text()',
        'date': '//div[contains(@class,"info")]/h2[contains(text(), ",") and contains(text(), "20")]/text()',
        'image': '//div[contains(@class, "video-tour")]/div/a/img/@src',
        'performers': '//div[contains(@class,"info")]/h2/span[contains(text(),"eaturing")]/following-sibling::a/text()',
        'tags': '',
        'external_id': r'.*/(.*)$',
        'trailer': '',
        'pagination': '/videos/all/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@id="updates"]/div[contains(@class, "lg-4")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "X-Art"

    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.replace("_", "-").strip()
        return search

    def get_description(self, response):
        description = ''
        desc_rows = self.process_xpath(
            response, self.get_selector_map('description')).getall()
        for desc_row in desc_rows:
            description = description + desc_row.strip()

        if description is not None:
            return description.replace('Description:', '').strip()
        return ""
