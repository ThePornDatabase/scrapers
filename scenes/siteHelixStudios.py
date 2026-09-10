import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHelixStudiosSpider(BaseSceneScraper):
    name = 'HelixStudios'
    network = 'Helix Studios'
    parent = 'Helix Studios'
    site = 'Helix Studios'

    cookies = [{"name":"ageConfirmed","value":"true"},{"name":"defaults","value":"{}"}]

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
    }

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[contains(@class,"description-content")]/p/text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y', '%b %d, %Y'],
        'image': '//link[@rel="image_src"]/@href',
        'performers': '//div[@class="video-performer"]/a//div[@class="performer-name"]/text()',
        'tags': '//span[contains(text(), "Tags:")]/following-sibling::a[@data-Label="Tag"]/text()',
        'external_id': r'/(\d+)/',
        'pagination': '/watch-newest-helix-studios-clips-and-scenes.html?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta=response.meta
        scenes = response.xpath('//div[@class="grid-item"]/article/div[1]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
    
    def get_duration(self, response):
        duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
