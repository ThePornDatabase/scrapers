import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class FillerDawnsPlaceSpider(BaseSceneScraper):
    name = 'FillerDawnsPlace'
    network = 'Manyvids'
    parent = 'Manyvids'
    site = 'manyvidsdawnsplace'

    start_urls = [
        'https://shop.dawnsplace.com',
    ]

    pagination = [
        '/store/index.php?route=product/category&path=16_305&page=%s',
        '/store/index.php?route=product/category&path=16_297&page=%s',
        '/store/index.php?route=product/category&path=16_295&page=%s',
        '/store/index.php?route=product/category&path=16_294&page=%s',
        '/store/index.php?route=product/category&path=16_293&page=%s',
        '/store/index.php?route=product/category&path=16_292&page=%s',
        '/store/index.php?route=product/category&path=16_296&page=%s',
        '/store/index.php?route=product/category&path=16_247&page=%s',
        '/store/index.php?route=product/category&path=16_243&page=%s',
        '/store/index.php?route=product/category&path=16_245&page=%s',
        '/store/index.php?route=product/category&path=16_139&page=%s',
        '/store/index.php?route=product/category&path=16_38&page=%s',
        '/store/index.php?route=product/category&path=16_33&page=%s',
        '/store/index.php?route=product/category&path=16_34&page=%s',
        '/store/index.php?route=product/category&path=16_36&page=%s',
        '/store/index.php?route=product/category&path=16_23&page=%s',
        '/store/index.php?route=product/category&path=16_24&page=%s',
        # ~ '/store/index.php?route=product/category&path=16_10&page=%s',
        '/store/index.php?route=product/category&path=16_27&page=%s',
    ]

    selector_map = {
        'pagination': '',
        'external_id': 'Scene',
    }

    def start_requests(self):
        for pagination in self.pagination:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta={'page': self.page, 'pagination': pagination}, headers=self.headers, cookies=self.cookies)

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
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        title = response.xpath('//h2/text()').get()
        scenedate = re.search(r'(\d{4})', title).group(1) + "-01-01"
        scenes = response.xpath('//div[@class="product-thumb"]')
        for scene in scenes:
            item = SceneItem()
            item['date'] = scenedate
            item['title'] = self.cleanup_title(scene.xpath('.//h4/a/text()').get())
            description = scene.xpath('.//div[@class="caption"]/p[1]/text()').getall()
            item['description'] = self.cleanup_description(" ".join(description)).replace("\n", "").replace("\r", "").replace("  ", "")
            item['description'] = re.sub(r'\d+:\d+min', '', item['description'])
            item['description'] = re.sub(r'\d+x\d+', '', item['description'])
            item['description'] = re.sub(r'\d+kbps', '', item['description'])
            item['description'] = item['description'].replace("@", "").replace("  ", "").replace("-", "").lstrip()
            item['image'] = scene.xpath('.//div[@class="image"]/a/img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            duration = scene.xpath('.//div[@class="caption"]/p[1]/text()').get()
            duration = re.search(r'(\d{1,2}:\d{1,2})\s?min', duration)
            if duration:
                item['duration'] = self.duration_to_seconds(duration.group(1))
            else:
                item['duration'] = None
            item['network'] = 'Manyvids'
            item['parent'] = 'Manyvids'
            item['site'] = 'manyvidsdawnsplace'
            item['url'] = scene.xpath('.//div[@class="image"]/a/@href').get()
            item['id'] = re.search(r'id=(\d+)', item['url']).group(1)
            item['tags'] = []
            item['performers'] = []
            item['trailer'] = ""
            yield item
