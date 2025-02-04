import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieTinoShopSpider(BaseSceneScraper):
    name = 'MovieTinoShop'
    network = 'Tino Media'
    parent = 'Tino Media'
    site = 'Tino Media'

    start_url = 'https://tinoshop.com'
    paginations = [
        '/en/Teens?cat=1&next_page=%s',
        '/en/Bi-DVDs?cat=1&next_page=%s',
        '/en/Gay?cat=2&next_page=%s',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '',
        'type': 'Movie',
    }


    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//table[@class="productPreview"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//h2/a/text()').get())
            item['date'] = None
            item['image'] = scene.xpath('.//a/img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['url'] = scene.xpath('.//h2/a/@href').get()
            item['tags'] = ['European']
            item['performers'] = []
            item['description'] = ""
            item['type'] = 'Movie'
            item['id'] = scene.xpath('.//input[@type="hidden" and @name="product"]/@value').get()
            item['trailer'] = None
            item['site'] = 'Tino Media'
            item['parent'] = 'Tino Media'
            item['network'] = 'Tino Media'
            yield item


