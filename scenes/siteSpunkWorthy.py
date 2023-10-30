import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSpunkWorthySpider(BaseSceneScraper):
    name = 'SpunkWorthy'
    network = 'SpunkWorthy'
    parent = 'SpunkWorthy'
    site = 'SpunkWorthy'

    start_urls = [
        'https://spunkworthy.com',
    ]

    selector_map = {
        'title': '//div[@class="head"]/p[1]/span/text()',
        'description': '//div[contains(@class,"video_synopsis")]/div[@class="vid_text"]/p[not(./a) and not(contains(./text(), "Tags"))]/text()',
        'image': '//div[@class="content"]/div[contains(@class, "video_player")]/img[contains(@src, ".jpg")]/@src|//div[contains(@class, "video_player")]/div/video/@poster',
        'performers': '//div[@class="scene_models"]/div/p/a/text()',
        'tags': '//div[contains(@class,"video_synopsis")]/div[@class="vid_text"]/p[contains(./text(), "Tags")]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/preview/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="vid"]')
        for scene in scenes:
            scenedate = scene.xpath('./comment()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{1,2} \w{3,4} \d{2})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %b %y']).strftime('%Y-%m-%d')
            scene = scene.xpath('./p/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers2 = []
        for performer in performers:
            performer = performer.lower().replace("more of ", "")
            performers2.append(string.capwords(performer))
        return performers2
