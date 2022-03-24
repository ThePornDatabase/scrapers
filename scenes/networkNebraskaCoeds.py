import re
from urllib.parse import urlparse
from datetime import date, timedelta
import scrapy

from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkNebraskaCoedsSpider(BaseSceneScraper):
    name = 'NebraskaCoeds'
    network = 'Nebraska Coeds'

    start_urls = [
        ['https://tour.nebraskacoeds.com/', '/categories/Movies_%s_d.html', 'Nebraska Coeds'],
        ['https://www.springbreaklife.com/', '/categories/Movies_%s_d.html', 'Spring Break Life'],
        ['https://tour.southbeachcoeds.com/', '/categories/Movies_%s_d.html', 'South Beach Coeds'],
        ['https://tour.afterhoursexposed.com/', '/categories/Movies_%s_d.html', 'After Hours Exposed'],
        ['https://tour.eurocoeds.com/', '/categories/Movies_%s_d.html', 'Euro Coeds'],
        ['https://tour.misspussycat.com/', '/categories/Movies_%s_d.html', 'Miss Pussycat'],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'view/(\d+)/',
        'trailer': '',
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1], 'site': link[2], 'url': link[0]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
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
                    url = meta['url']
                    yield scrapy.Request(url=self.get_next_page_url(url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta

        scenes = response.xpath('//div[@class="updateThumb"]/a[contains(@href,"/trailers/")]/../..|//div[@class="updateItem"]/a[contains(@href,"/trailers/")]/..|//div[@class="updateItem"]/a[contains(@href,"content/")]/..')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div/h5/a/text()|./div/h4/a/text()').get()
            if title:
                item['title'] = title.strip()
            else:
                item['title'] = ''

            scenedate = scene.xpath('.//span[@class="availdate"]/text()|.//p/span[2]/text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate.strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('.//span[@class="tour_update_models"]/a/text()|.//p/span[1]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                item['performers'] = []

            image = scene.xpath('./div[@class="updateThumb"]/a/img/@src|./a/img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('./div[@class="updateThumb"]/a/@onclick|./a/@onclick').get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*.mp4)\'', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    uri = urlparse(response.url)
                    base = uri.scheme + "://" + uri.netloc
                    item['trailer'] = base + trailer.strip()
            else:
                item['trailer'] = ''

            url = scene.xpath('./div[@class="updateThumb"]/a/@href|./a/@href').get()
            if url:
                item['url'] = url.strip()
                item['id'] = re.search(r'.*/(.*).html', item['url']).group(1)
                item['id'] = item['id'].lower().strip()
            else:
                item['url'] = ''
                item['id'] = ''

            item['description'] = ''
            item['tags'] = []

            item['site'] = meta['site']
            item['parent'] = meta['site']
            item['network'] = "Nebraska Coeds"

            if item['id'] and item['title']:
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
