import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Site18YogaSpider(BaseSceneScraper):
    name = '18Yoga'
    network = "18Yoga"
    parent = "18Yoga"

    start_urls = [
        'https://18yoga.com',
    ]

    selector_map = {
        'title': '//div[@class="small-12 columns"]/h2/text()',
        'description': '//div[@class="small-12 columns"]/p/text()',
        'date': '',
        'image': '//div[@class="image"]/a/img/@src',
        'performers': '//ul[@class="scene-meta"]//a[contains(@href,"/girl/")]/text()',
        'tags': '',
        'external_id': r'video\/([0-9]+)',
        'duration': '//ul[@class="scene-meta"]/li/b[contains(text(),"Duration")]/../text()',
        're_duration': r'(?P<minutes>[0-9]+)[^0-9]+(?P<seconds>[0-9]+)',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):
        link = "https://18yoga.com/videos"
        yield scrapy.Request(link, callback=self.get_scenes)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"video-list")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = self.cleanup_text(self.get_element(response, 'duration'))

        regexp, group, mod = self.get_regex(self.regex['re_duration'])
        match = regexp.search(duration)

        if match:
            return int(match.group("minutes")) * 60 + int(match.group("seconds"))

        return ''
