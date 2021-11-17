import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBoundHoneysSpider(BaseSceneScraper):
    name = 'BoundHoneys'
    network = 'Bound Honeys'
    parent = 'Bound Honeys'
    site = 'Bound Honeys'

    start_urls = [
        'http://boundhoneys.com',
    ]

    selector_map = {
        'title': '//div[@class="updateVideoTitle"]/text()',
        'description': '//div[@class="updateDescription"]//text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//div[@class="updateModelsList"]/a/text()',
        'tags': '//div[contains(@class, "updateCategoriesList")]/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/bondage-videos.php?perpage=24&id=999&p=%s#videos'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update"]')
        for scene in scenes:
            date = scene.xpath('./div[@class="updateDate"]/text()')
            if date:
                date = self.parse_date(date.get()).isoformat()
            else:
                date = self.parse_date('today').isoformat()
            scene = scene.xpath('./a/@href').get()
            if scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_description(self, response):
        description = super().get_description(response)
        description = re.sub(r'^Action ', ' ', description)
        return self.cleanup_description(description)

    def get_id(self, response):
        externid = response.xpath('//script[contains(text(), "updateIDForPlayer")]/text()')
        if externid:
            externid = externid.get()
            externid = re.search(r'updateIDForPlayer.*?(\d{1,4})', externid)
            if externid:
                return externid.group(1).strip()
        externid = response.xpath('//script[contains(text(), "gtag")]/text()')
        if externid:
            externid = externid.get()
            externid = re.search(r'name.*?(\d{1,4})', externid)
            if externid:
                return externid.group(1).strip()

        return None
