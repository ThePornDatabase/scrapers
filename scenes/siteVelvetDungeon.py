import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteVelvetDungeonSpider(BaseSceneScraper):
    name = 'VelvetDungeon'
    site = 'Velvet Dungeon'
    parent = 'Velvet Dungeon'
    network = 'Velvet Dungeon'

    cookies = [{"domain": "www.thevelvetdungeon.com", "name": "age_gate", "path": "/", "sameSite": "no_restriction", "secure": true, "session": false, "storeId": "0", "value": "18"}]

    start_urls = [
        'https://www.thevelvetdungeon.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//p[contains(@class, "has-text-align-center")]/following-sibling::p/text()',
        'date': '//time[contains(@class, "published")]/@datetime',
        'image': '//div[@class="post-thumbnail default"]/img/@src',
        'performers': '//span[@class="tags-links"]/a/text()',
        'tags': '//span[@class="cat-links"]/a/text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/',
        'pagination': '/new-releases/page/%s/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(@class, "entry-title")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.remove("Video")
        return tags

    def get_duration(self, response):
        duration = response.xpath('//p[contains(text(), "minutes")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
