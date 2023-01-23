import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMyPornBabesSpider(BaseSceneScraper):
    name = 'MyPornBabes'
    network = 'My Porn Babes'
    parent = 'My Porn Babes'
    site = 'My Porn Babes'

    start_urls = [
        'https://mypornbabes.com',
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
        'pagination': '/girls/?modelgallery_id=all&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse_model_page, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def parse_model_page(self, response, **kwargs):
        meta = response.meta
        models = response.xpath('//div[@class="contentimg"]')
        for model in models:
            modelurl = self.format_link(response, model.xpath('./a/@href').get())
            modelname = model.xpath('./a/h4/text()').get()
            if modelname:
                modelname = modelname.strip()
                meta['name'] = modelname
            if modelurl and modelname:
                yield scrapy.Request(url=modelurl, callback=self.parse_model_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and len(models):
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse_model_page, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_model_scenes(self, response):
        scenes = response.xpath('//div[@class="contentimg"]/a/@href').getall()
        scenes = response.xpath('//div[@class="contentimg"]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = [response.meta['name']]
            title = scene.xpath('.//h4/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = 'No Title Available'

            item['description'] = self.cleanup_description(scene.xpath('.//p/text()').get())

            item['site'] = "My Porn Babes"
            item['parent'] = "My Porn Babes"
            item['network'] = "My Porn Babes"
            item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//img/@src').get()
            if image:
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = None
            item['tags'] = []
            item['duration'] = None
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
            item['id'] = re.search(r'.*/(\d+)', item['url']).group(1)
            yield item
