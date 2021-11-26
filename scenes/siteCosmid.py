import re
from datetime import date, timedelta
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
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = 'No Title Available'

            item['description'] = ''

            item['site'] = "Cosmid"
            item['parent'] = "Cosmid"
            item['network'] = "Cosmid"

            scenedate = scene.xpath('./div[contains(@class,"item-info")]/div[@class="date"]/text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate, date_formats=['%Y-%m-%d']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//div[contains(@class,"videothumb")]/img/@src').get()
            if image:
                item['image'] = "https://cosmid.net" + image.replace('//', '/').replace('#id#', '').strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('.//div[contains(@class,"videothumb")]/video/source/@src').get()
            if trailer:
                item['trailer'] = "https://cosmid.net" + trailer.replace(" ", "%20").replace('#id#', '').strip()
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
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item
