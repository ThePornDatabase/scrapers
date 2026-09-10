import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteRandyBlueSpider(BaseSceneScraper):
    name = 'RandyBlue'
    network = 'RandyBlue'
    parent = 'RandyBlue'
    site = 'RandyBlue'

    start_urls = [
        'https://www.randyblue.com',
    ]

    # The div.title-zone block is gone, but the player still carries a full
    # schema.org VideoObject as microdata, which is the sturdier source anyway.
    selector_map = {
        'title': '//*[@itemprop="name"]/@content|//*[@itemprop="name"]/text()',
        'description': '//*[@itemprop="description"]/@content|//*[@itemprop="description"]/text()',
        'date': '//*[@itemprop="uploadDate"]/@content|//*[@itemprop="uploadDate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//*[@itemprop="thumbnailUrl"]/@content|//*[@itemprop="thumbnailUrl"]/text()',
        'performers': '//*[contains(@class, "scene-models")]//a/text()',
        'tags': '//*[contains(@class, "scene-tags")]//a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'scenes/(.*)\.htm',
        'pagination': '/categories/videos_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # the card is still an li.scene-video, but its link is no longer a direct
        # li > div > a child -- it sits inside a section.previewThumb
        scenes = response.xpath('//li[contains(@class, "scene-video")]//a[contains(@href, "/scenes/")]/@href').getall()
        scenes = list(dict.fromkeys(scenes))
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
