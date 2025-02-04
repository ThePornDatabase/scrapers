import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class PublicFlashFullImportSpider(BaseSceneScraper):
    name = 'PublicFlash'

    start_urls = [
        'https://www.publicflash.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/models/%s/popular/'
    }

    def start_requests(self):

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse_model_page,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_model_page(self, response, **kwargs):
        meta = response.meta
        models = response.xpath('//div[@class="modelimage"]/..')
        for model in models:
            modelurl = model.xpath('.//h3/a/@href').get()
            modelname = model.xpath('.//h3/a/text()').get()
            modelimage = model.xpath('.//img/@src0_1x').get()
            meta['modelimage'] = self.format_link(response, modelimage).replace("-1x", "-full")
            meta['modelimage_blob'] = self.get_image_blob_from_link(meta['modelimage'])

            if modelname:
                modelname = modelname.strip()
                meta['name'] = modelname
            if modelurl and modelname:
                yield scrapy.Request(url=modelurl,
                                     callback=self.parse_model_scenes,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and len(models):
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                 callback=self.parse_model_page,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_model_scenes(self, response):
        meta = response.meta
        modelname = meta['name']
        scenes = response.xpath('//div[contains(@class,"update-table")]')
        for scene in scenes:
            item = self.init_scene()
            item['performers'] = scene.xpath('.//span[contains(@class, "update_models")]/a/text()').getall()
            title = scene.xpath('.//h3/a/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = 'No Title Available'

            item['description'] = ''

            item['site'] = "PublicFlash"
            item['parent'] = "PublicFlash"
            item['network'] = "PublicFlash"
            item['tags'] = scene.xpath('.//span[contains(@class, "update-tags")]/a/text()').getall()
            item['image'] = scene.xpath('.//div[contains(@class, "update-col-left")]/a/img/@src0_1x').get()
            item['image'] = self.format_link(response, item['image']).replace("-1x", "-full")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['performers_data'] = []
            performer_extra = {}
            performer_extra['name'] = modelname
            performer_extra['site'] = "PublicFlash"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performer_extra['image'] = meta['modelimage']
            performer_extra['image_blob'] = meta['modelimage_blob']

            item['performers_data'].append(performer_extra)

            duration = scene.xpath('.//span[contains(@class, "update-runtime")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    item['duration'] = self.duration_to_seconds(duration.group(1))

            sceneid = scene.xpath('.//div[contains(@class, "update-col-left")]/a/img/@id').get()
            item['id'] = re.search(r'target-(\d+)-', sceneid).group(1)
            item['site'] = "PublicFlash"
            item['parent'] = "PublicFlash"
            item['network'] = "PublicFlash"
            item['type'] = "Scene"
            item['url'] = response.url
            yield item
