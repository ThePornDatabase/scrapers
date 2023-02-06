import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMenAtPlaySpider(BaseSceneScraper):
    name = 'MenAtPlay'
    network = 'Men At Play'
    parent = 'Men At Play'
    site = 'Men At Play'

    start_urls = [
        'https://menatplay.com',
    ]

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403, 302],
    }

    selector_map = {
        'title': '//h1/text()',
        'description': '//p[@id="textDesc"]/text()',
        'date': '//span[@class="availdate" and contains(text(), ",")]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"gallery_info")]//span[@class="tour_update_models"]/a/text()',
        'tags': '//div[contains(@class,"gallery_info")]//a[@class="tagsVideoPage"]/text()',
        'duration': '//span[@class="availdate" and contains(text(), "min")]/text()',
        're_duration': r'(.*)? ?[Mm]in',
        'trailer': '//div[@class="fullscreenTour"]//source/@src',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateDetails"]')
        for scene in scenes:
            sceneid = scene.xpath('.//a/img/@id')
            if sceneid:
                sceneid = sceneid.get()
                sceneid = re.search(r'(\d+)', sceneid).group(1)
            scene = scene.xpath('./a/@href').get()
            if not sceneid:
                sceneid = re.search(r'updates/(.*)?\.htm', scene).group(1)
            meta['id'] = sceneid
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
