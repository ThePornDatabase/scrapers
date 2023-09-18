import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePinupFilesSpider(BaseSceneScraper):
    name = 'PinupFiles'
    network = 'Pinup Files'
    parent = 'Pinup Files'
    site = 'Pinup Files'

    start_urls = [
        'https://www.pinupfiles.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="update-info-block"]/h3/following-sibling::text()',
        'date': '//strong[contains(text(),"Added")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[@class="player-time"]/text()',
        'performers': '//div[contains(@class, "models-list-thumbs")]//a[contains(@href, "/models/")]/span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'external_id': r'',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video playsinline src=\"(.*?)\"',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "_videothumb_")]|//div[@class="item-thumb"]/a/@href/../..')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            if re.search(r'(\w\d+)_', sceneid):
                meta['id'] = re.search(r'(\w\d+)_', sceneid).group(1)
            else:
                sceneid = scene.xpath('./a/img/@id')
                if sceneid:
                    sceneid = sceneid.get()
                    sceneid = re.search(r'-(\d+)$', sceneid)
                    if sceneid:
                        meta['id'] = "b" + sceneid.group(1)
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
