import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class EvolvedFightsSpider(BaseSceneScraper):
    name = 'EvolvedFights'
    site = 'Evolved Fights'
    parent = 'Evolved Fights'
    network = 'Evolved Fights'

    start_urls = [
        'https://www.evolvedfights.com',
        # 'https://www.evolvedfightslez.com', Moved to its own scraper
    ]

    selector_map = {
        'title': '//div[contains(@class, "Title")]/h4/text()',
        'description': '//div[contains(@class, "vidImgContent ")]/p/text()',
        'performers': '//div[@class="latestUpdateBinfo gallery_info bg_light radius"]/p[@class="link_light"]/a[@class="link_bright infolink"]/text()',
        'date': '//div[@class="vidImgTitle"]/div[@class="latestUpdateBinfo gallery_info bg_light radius"]/ul[@class="videoInfo"]//comment()[contains(., "Date")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[@class="blogTags"]/ul/li/a/text()',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '//script[contains(text(), "trailer")]/text()',
        're_trailer': r'trailer.*?path.*?[\'\"](.*?)[\'\"]',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="vidImgTitle"]/div[@class="latestUpdateBinfo gallery_info bg_light radius"]/ul[@class="videoInfo"]/li[@class="text_med"]/text()[contains(., "min")]')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^0-9a-z]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None
