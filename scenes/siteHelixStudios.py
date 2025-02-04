import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHelixStudiosSpider(BaseSceneScraper):
    name = 'HelixStudios'
    network = 'Helix Studios'
    parent = 'Helix Studios'
    site = 'Helix Studios'

    start_urls = [
        'https://www.helixstudios.com',
    ]

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    selector_map = {
        'title': '//h1/text()|//div[contains(@class,"video-header")]/div[@class="video-info"]/span[1]/text()',
        'description': '//div[contains(@class,"description-content")]/p/text()',
        'date': '//div[@class="info-items"]/span[@class="info-item date"]/text()',
        'date_formats': ['%B %d, %Y', '%b %d, %Y'],
        'image': '//img[@id="titleImage"]/@src|//div[@class="player-wrapper"]//div[contains(@class, "spark")]/video/@poster',
        'performers': '//div[@class="video-cast"]//h4/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'duration': '',
        'trailer': '//div[@class="player-wrapper"]//div[contains(@class, "spark")]/video/source/@src',
        'external_id': r'video/(\d+)/',
        'pagination': '/videos/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="grid-item-wrapper"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath('//meta[@name="keywords"]/@content')
        if tags:
            performers = self.get_performers(response)
            taglist = tags.get()
            taglist = taglist.split(",")
            tags = []
            for tag in taglist:
                if tag.strip() not in performers:
                    tags.append(self.cleanup_title(tag.strip()))
        return tags

    def get_duration(self, response):
        duration = response.xpath('//div[@class="info-items"]/span[contains(text(), "min")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
