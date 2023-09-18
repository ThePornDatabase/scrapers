import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class Only3XSpider(BaseSceneScraper):
    name = 'Only3X'
    network = 'Only 3X'
    parent = 'Only 3X'

    start_urls = [
        'https://only3x.com'
    ]

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//div[@class="synopsis"]//text()',
        'date': '//span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'duration': '//span[contains(text(), "Length")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a//text()',
        'tags': '//span[contains(text(), "Tags")]/following-sibling::a[@data-label="Tag"]/text()',
        'external_id': r'/(\d+)/',
        'trailer': '',
        'pagination': '/watch-newest-only-3x-clips-and-scenes.html?page=%s&hybridview=member'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/div/a/@href').getall()
        for scene in scenes:
            parsescene = True
            link = self.format_link(response, scene)
            with open('dupelist-only3x.txt', 'r', encoding="utf-8") as file1:
                for i in file1.readlines():
                    if link in i:
                        # ~ print(f"Already scraped scene: {link}")
                        parsescene = False
                        break
            if parsescene and re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//span[contains(text(), "Studio:")]/following-sibling::span/text()')
        if site:
            return site.get().strip()
        super.get_site(response)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            scenelength = 0
            duration = duration.get()
            if "min" in duration:
                duration = re.search(r'(\d+) min', duration)
                if duration:
                    minutes = duration.group(1)
                    scenelength = scenelength + (int(minutes) * 60)
            return str(scenelength)
        return ""
