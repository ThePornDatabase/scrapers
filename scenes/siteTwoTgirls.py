import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTwoTgirlsSiteSpider(BaseSceneScraper):
    name = 'TwoTgirls'
    network = 'Two Tgirls'

    start_urls = [
        'https://twotgirls.com',
        'https://tgirlplaytime.com'
    ]

    selector_map = {
        'title': '//div[contains(@class, "video-details")]/h1/text()',
        'description': '//div[contains(@class, "video-details")]/p[1]/text()',
        'date': '//p[@class="video-date"]/text()',
        're_date': r'(\w+ \d{1,2}\w{0,2}, \d{4})',
        'image': '//div[@class="container"]//video/@poster',
        'image_blob': True,
        'performers': '//div[contains(@class, "video-details")]/p[@class="video-date"]/a/text()',
        'tags': '//div[contains(@class, "video-details")]/p[@class="video-tags"]/a/text()',
        'external_id': r'.*video/(.*)',
        'trailer': '',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article[@class="shadow video"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = super().get_site(response)
        if "twotgirls" in response.url:
            return "Two TGirls"
        if "tgirlplaytime" in response.url:
            return "TGirl Playtime"
        return site

    def get_parent(self, response):
        parent = super().get_site(response)
        if "twotgirls" in response.url:
            return "Two TGirls"
        if "tgirlplaytime" in response.url:
            return "TGirl Playtime"
        return parent

    def get_date(self, response):
        date = response.xpath(self.get_selector_map('date')).getall()
        date = date = "".join(date)
        date = re.search(self.get_selector_map('re_date'), date)
        if date:
            return self.parse_date(date.group(1)).isoformat()
        return self.parse_date('today').isoformat()
