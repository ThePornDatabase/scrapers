import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotBabes4kSpider(BaseSceneScraper):
    name = 'HotBabes4k'

    start_urls = [
        'https://hotbabes4k.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/models/models_%s_d.html'
    }

    def parse(self, response, **kwargs):
        scenes = self.get_models(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_models(self, response):
        meta = response.meta
        models = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for model in models:
            yield scrapy.Request(self.format_link(response, model), callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div/div/div[contains(@class,"time")]/../..')
        for scene in scenes:
            photocheck = scene.xpath('./div/div[contains(@class,"time") and contains(text(), "Pics")]/text()')
            if not photocheck:
                item = SceneItem()

                title = scene.xpath('./h4/a/text()')
                if title:
                    item['title'] = self.cleanup_title(title.get())
                else:
                    item['title'] = None

                description = scene.xpath('.//p/text()')
                if description:
                    item['description'] = description.get()
                else:
                    item['description'] = None

                image = scene.xpath('.//img/@src')
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    item['id'] = re.search(r'.*/(\d+)', item['image']).group(1)
                else:
                    item['image'] = None
                    item['image_blob'] = None
                    item['id'] = None

                duration = scene.xpath('.//div[contains(@class,"time")]/text()')
                if duration:
                    item['duration'] = self.duration_to_seconds(duration.get())
                else:
                    item['duration'] = None

                item['date'] = self.parse_date('today').isoformat()
                item['tags'] = ['Babe']

                performers = response.xpath('//div[contains(@class, "modelBioTitle")]/span/text()')
                if performers:
                    item['performers'] = performers.getall()
                else:
                    item['performers'] = []

                item['trailer'] = None
                item['site'] = 'Hot Babes 4k'
                item['parent'] = 'Hot Babes 4k'
                item['network'] = 'Hot Babes 4k'
                item['url'] = response.url

                if item['title'] and item['id']:
                    yield item
