import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJodiWestClipsSpider(BaseSceneScraper):
    name = 'JodiWestClips'
    network = 'Jodi West Clips'
    parent = 'Jodi West Clips'
    site = 'Jodi West Clips'

    start_urls = [
        'https://www.jodiwest.com',
    ]

    cookies = [
        {
            "name": "ageConfirmed",
            "value": "true"
        }, {
            "name": "use_lang",
            "value": "val=en"
        }, {
            "name": "defaults",
            "value": "{'hybridView':''}"
        }
    ]

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '',
        'date': '//span[contains(text(), "Released:")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class,"video-performer-name")]/span/text()',
        'tags': '//span[contains(text(), "Tags:")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'shop/(\d+)/',
        'pagination': '/watch-streaming-video-by-scene.html?sort=released&page=%s&studio=94771',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None
