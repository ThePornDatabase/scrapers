import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBukkakeLatinSpider(BaseSceneScraper):
    name = 'BukkakeLatin'
    network = 'BukkakeLatin'
    parent = 'BukkakeLatin'
    site = 'BukkakeLatin'

    start_urls = [
        'https://www.bukkakelatin.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//p[@itemprop="description"]//text()',
        'date': '//div[@class="video-views"]/text()[contains(., "/")]',
        're_date': r'(\d{2}/\d{2}/\d{2})',
        'date_formats': ['%m/%d/%y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'duration': '',
        'external_id': r'',
        'pagination': '/videos/latest?page_id=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "video-latest-list")]')
        for scene in scenes:
            sceneid = scene.xpath('./@data-id').get()
            if sceneid:
                meta['id'] = sceneid.strip()

            sceneurl = scene.xpath('./div[1]/a/@href').get()
            if sceneurl:
                meta['url'] = self.format_link(response, sceneurl.strip())

            if meta['id'] and meta['url']:
                yield scrapy.Request(url=meta['url'], callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Bukakke', 'Latin']