import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class ScorelandSpider(BaseSceneScraper):
    name = 'Scoreland'
    site = 'Scoreland'
    parent = 'Scoreland'
    network = 'ScorePass'

    start_urls = [
        'https://www.scoreland.com',
    ]

    selector_map = {
        'title': '//main/div/section/div[@class="row"]/div/h1/text()|//section[@id="videos_page-page"]/div[contains(@class,"ali-center")]//h2/text()',
        'description': '//div[contains(@class, "p-desc")]//text()',
        'date': '//div[contains(@class,"p-info")]//span[contains(text(), "Date:")]/following-sibling::span/text()',
        'date_format': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"p-info")]//span[contains(text(), "Featuring:")]/following-sibling::span/a/text()',
        'tags': '//h3[contains(text(), "Tags")]/following-sibling::div[1]/a/text()',
        'duration': '//div[contains(@class,"p-info")]//span[contains(text(), "Duration:")]/following-sibling::span/text()',
        'external_id': r'.*/(\d+)/',
        'trailer': '//div[contains(@class, "mr-lg")]//video/source[1]/@src',
        'pagination': '/big-boob-videos/?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "li-item video")]/div/div/a/@href').getall()
        for scene in scenes:
            # ~ if re.match(r'.*\?nats=', scene):
                # ~ scene = re.search(r'(.*)\?nats=', scene).group(1)
            if "step=signup" not in scene and "join." not in scene:
                yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)
