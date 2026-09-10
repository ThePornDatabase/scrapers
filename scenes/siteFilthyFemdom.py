import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFilthyFemdomSpider(BaseSceneScraper):
    name = 'FilthyFemdom'
    network = 'FilthyFemdom'
    parent = 'FilthyFemdom'
    site = 'FilthyFemdom'

    start_urls = [
        'https://filthyfemdom.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p[1]//text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "featuring")]/ul/li[contains(@class, "update_models")]/a/text()',
        'tags': '//div[contains(@class, "featuring")]/ul/li[not(contains(@class, "update_models"))]/a/text()',
        'external_id': r'',
        'pagination': '/categories/movies/%s/latest/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="item-thumb"]/div[1]')
        for scene in scenes:
            sceneid = scene.xpath('./@class').get()
            meta['id'] = re.search(r'(\d+)_videothumb', sceneid).group(1)

            scene = scene.xpath('./a/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "videoInfo")]/p[contains(text(), "of video")]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace("&nbsp;", " ").replace("\xa0", " ").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None
    
    def get_image(self, response):
        image = super().get_image(response)
        if "-1x" in image:
            image = image.replace("-1x", "-4x")
        if "-2x" in image:
            image = image.replace("-2x", "-4x")
        return image