import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHerSweetHandSpider(BaseSceneScraper):
    name = 'HerSweetHand'
    network = 'HerSweetHand'
    parent = 'HerSweetHand'
    site = 'HerSweetHand'

    start_urls = [
        'https://hersweethand.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/page%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-card"]')
        for scene in scenes:
            item = self.init_scene()
            title = scene.xpath('.//h2/text()').get()
            item['title'] = string.capwords(self.cleanup_title(title))

            image = scene.xpath('./div[contains(@class, "video-card-img")]/a/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['url'] = self.format_link(response, scene.xpath('./div[contains(@class, "video-card-img")]/a/@href').get())
            item['id'] = re.search(r'/video/(.*)/?$', item['url']).group(1)
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network

            yield item