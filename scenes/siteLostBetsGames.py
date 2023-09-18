import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLostBetsGamesSpider(BaseSceneScraper):
    name = 'LostBetsGames'
    network = 'Lost Bets Games'
    parent = 'Lost Bets Games'
    site = 'Lost Bets Games'

    start_urls = [
        'https://lostbetsgames.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "descriptions")]/h1/text()',
        'description': '//div[contains(@class, "descriptions")]//p//text()',
        'image': '//video/@poster',
        'performers': '',
        'tags': '',
        'trailer': '//video/source/@src',
        'external_id': r'id/(\d+)/',
        'pagination': '/site/index/p/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//figure')
        for scene in scenes:
            scenedate = scene.xpath('.//em[@class="added"]/time/@datetime')
            if scenedate:
                meta['date'] = scenedate.get()
            duration = scene.xpath('.//span[@class="time"]//time/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
