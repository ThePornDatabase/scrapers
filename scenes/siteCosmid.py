import re
import html
import string
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class CosmidFullImportSpider(BaseSceneScraper):
    name = 'Cosmid'
    network = 'Cosmid'
    parent = 'Cosmid'

    start_urls = [
        'https://cosmid.net/'
    ]

    selector_map = {
        'title': "",
        'description': "",
        'date': "",
        'performers': "",
        'tags': "",
        'external_id': '',
        'image': '',
        'trailer': '',
        'pagination': '/models/%s/latest/'
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
        models = response.xpath('//div[@class="item-portrait"]//h4')
        for model in models:
            modelurl = model.xpath('./a/@href').get()
            modelname = model.xpath('./a/text()').get()
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
        modelname = response.meta['name']
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = [modelname]
            title = scene.xpath('./div[contains(@class,"item-info")]/h4/a/text()').get()
            if title:
                item['title'] = string.capwords(title.strip())
                item['title'] = html.unescape(item['title'])
            else:
                item['title'] = 'No Title Available'

            item['description'] = ''

            item['site'] = "Cosmid"
            item['parent'] = "Cosmid"
            item['network'] = "Cosmid"

            date = scene.xpath('./div[contains(@class,"item-info")]/div[@class="date"]/text()').get()
            if date:
                date = dateparser.parse(date.strip()).isoformat()
                item['date'] = date
            else:
                item['date'] = "1970-01-01T00:00:00"

            image = scene.xpath('.//div[contains(@class,"videothumb")]/img/@src').get()
            if image:
                image = image.replace(r'//', '/').strip()
                image = image.replace(r'#id#', '').strip()
                image = "https://cosmid.net" + image
                item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('.//div[contains(@class,"videothumb")]/video/source/@src').get()
            if trailer:
                trailer = "https://cosmid.net" + trailer.strip()
                trailer = trailer.replace(" ", "%20")
                trailer = trailer.replace(r'#id#', '').strip()
                item['trailer'] = trailer.strip()
            else:
                item['trailer'] = ''

            externalid = title.replace("_", "-").strip().lower()
            externalid = externalid.replace("  ", " ")
            externalid = externalid.replace(" ", "-")
            externalid = re.sub('[^a-zA-Z0-9-]', '', externalid)
            if externalid:
                item['id'] = externalid
            else:
                item['id'] = ''

            item['tags'] = []

            item['url'] = response.url

            if item['id'] and item['title'] and item['date']:
                yield item
