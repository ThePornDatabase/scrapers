import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSinnistarSpider(BaseSceneScraper):
    name = 'Sinnistar'
    network = 'Sinnistar'
    parent = 'Sinnistar'
    site = 'Sinnistar'

    start_urls = [
        'https://sinnistar.com',
    ]

    selector_map = {
        'title': './/h2/text()',
        'description': './/h2/following-sibling::p[1]//text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="gallerygrid"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = ''
            item['performers'] = []
            item['tags'] = []
            item['url'] = scene.xpath('./a/@href').get()
            item['id'] = re.search(r'.*/(.*?)\.htm', item['url']).group(1)
            image = scene.xpath('./a/img/@src').get()
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['type'] = 'Scene'
            item['trailer'] = ''
            item['site'] = "Sinnistar"
            item['parent'] = "Sinnistar"
            item['network'] = "Sinnistar"

            yield item
