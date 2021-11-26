import re
import string
from datetime import date, timedelta
from urllib.parse import urlparse
import scrapy
from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPureCFNMSpider(BaseSceneScraper):
    name = 'PureCFNM'
    network = 'Pure CFNM'
    parent = 'Pure CFNM'

    start_urls = [
        ['https://www.purecfnm.com', '/categories/purecfnm_%s_d.html', 'Pure CFNM'],
        ['https://www.ladyvoyeurs.com', '/categories/lady-voyeurs_%s_d.html', 'Lady Voyeurs'],
        ['https://www.amateurcfnm.com', '/categories/amateur-cfnm_%s_d.html', 'Amateur CFNM'],
        ['https://www.cfnmgames.com', '/categories/cfnm-games_%s_d.html', 'CFNM Games'],
        ['https://www.girlsabuseguys.com', '/categories/girls-use-guys_%s_d.html', 'Girls Abuse Guys'],
        ['https://littledick.club', '/categories/movies_%s_d.html', 'Little Dick Club'],
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
        'pagination': '/videos?order=publish_date&sort=desc&page=%s'
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

        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)

            scenedate = scene.xpath('.//div[contains(@class,"update_date")]/comment()/following-sibling::text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate.strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('.//span[@class="update_models"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            image = scene.xpath('./a/img/@data-src0_3x').get()
            if not image:
                image = scene.xpath('./a/img/@data-src0_2x').get()
            if not image:
                image = scene.xpath('./a/img/@data-src0_1x').get()
            if not image:
                image = scene.xpath('./a/img/@src').get()
            if image:
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                item['image'] = base + image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a[contains(@onclick,"/trailer/")]/@onclick').get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*.mp4)\'', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    uri = urlparse(response.url)
                    base = uri.scheme + "://" + uri.netloc
                    item['trailer'] = base + trailer.strip()
            else:
                item['trailer'] = ''

            item['id'] = scene.xpath('./@data-setid').get()
            item['url'] = response.url
            item['description'] = ''
            item['tags'] = []
            item['site'] = meta['site']
            item['parent'] = meta['site']
            item['network'] = "Pure CFNM"

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
