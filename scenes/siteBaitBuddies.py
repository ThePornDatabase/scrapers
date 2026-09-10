import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteBaitBuddiesSpider(BaseSceneScraper):
    name = 'BaitBuddies'
    network = 'Bait Buddies'
    parent = 'Bait Buddies'
    site = 'Bait Buddies'

    start_urls = [
        'https://www.baitbuddies.com',
    ]

    cookies = [{"domain":"www.baitbuddies.com","hostOnly":true,"httpOnly":false,"name":"welcome","path":"/","sameSite":"unspecified","secure":false,"session":true,"storeId":"0","value":"true"}]

    selector_map = {
        'description': '//div[@id="description"]//text()',
        'image': '//script[contains(text(), "posterImage")]/text()',
        're_image': r'posterImage:\s*["\'](https?://[^"\']+\.jpg)["\']',
        'performers': '//div[contains(@class, "new-video-models")]/div[contains(@class, "new-video-model")]//a/text()',
        'tags': '//div[@class="tags-box"]/a/text()',
        'external_id': r'.*/(\w+)-',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="blockHolder"]')
        for scene in scenes:
                scenedate = scene.xpath('.//b[contains(text(), "Date")]/following-sibling::text()')
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.get(), date_formats=['%m/%d/%y']).strftime('%Y-%m-%d')
                scene = scene.xpath('./a/@href').get()
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        performers = self.get_performers(response)
        return " and ".join(performers)
