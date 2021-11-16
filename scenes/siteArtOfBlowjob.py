import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteArtOfBlowjobSpider(BaseSceneScraper):
    name = 'ArtOfBlowjob'
    network = 'Art of Blowjob'
    parent = 'Art of Blowjob'
    site = 'Art of Blowjob'

    start_urls = [
        'https://theartofblowjob.com/',
    ]

    selector_map = {
        'title': '//div[@class="section_title"]/text()',
        'description': '//div[contains(@class,"preserve-newlines")]/text()',
        'date': '',
        'image': '//section[@id="about"]/img/@src',
        'performers': '',
        'tags': '',
        'external_id': r'videos/(\d+)/',
        'trailer': '',
        'pagination': '/display/updatelist/'
    }

    def start_requests(self):
        url = "https://www.theartofblowjob.com/display/updatelist/"
        yield scrapy.Request(url, callback=self.get_scenes, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="video-thumbnail"]/../../span/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        return ['Blowjob']
