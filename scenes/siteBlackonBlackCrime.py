import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackonBlackCrimeSpider(BaseSceneScraper):
    name = 'BlackonBlackCrime'
    network = 'D&E Media'
    parent = 'D&E Media'
    site = 'Black on Black Crime'

    start_urls = [
        'https://tour5m.blackonblackcrime.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"videoDetails")]/p/text()',
        'image': '//div[@class="player-thumb"]/img/@src0_2x',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-video hover"]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="time"]/text()')
            if duration:
                duration = re.search(r"(\d{1,2}:\d{2})", duration.get()).group(1)
                meta['duration'] = self.duration_to_seconds(duration)
            scenedate = scene.xpath('.//comment()[contains(., "date")]')
            if scenedate:
                scenedate = re.search(r"(\d{4}-\d{2}-\d{2})", scenedate.get()).group(1)
                meta['date'] = self.parse_date(scenedate, date_formats=['%Y-%m-%d']).isoformat()
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = response.xpath('//meta[@name="keywords"]/@content').get()
        title = response.xpath('//h1/text()').get()
        title = string.capwords(title).strip()
        if tags:
            tags = tags.split(",")
            tags = tags = list(map(lambda x: string.capwords(x.strip()), tags))
            if "Black On Black Crime" in tags:
                tags.remove("Black On Black Crime")
            if title in tags:
                tags.remove(title)
        return tags
