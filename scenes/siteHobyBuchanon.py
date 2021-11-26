import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class HobyBuchanonSpider(BaseSceneScraper):
    name = 'HobyBuchanon'
    network = 'Hoby Buchanon'
    parent = 'Hoby Buchanon'

    start_urls = [
        'https://hobybuchanon.com',
    ]

    pagination = [
        '/updates/page/%s/',
        '/behind-the-scenes/page/%s/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*\/(.*?)\/$',
        'trailer': '',
        'pagination': '/updates/page/%s/'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for pagination in self.pagination:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination),
                                     callback=self.parse,
                                     meta={'page': self.page, 'pagination': pagination},
                                     headers=self.headers,
                                     cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenelist = []
        scenes = response.xpath('//div[contains(@class,"post-item")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['image'] = None
            item['image_blob'] = None
            item['description'] = ''
            item['network'] = "Hoby Buchanon"
            item['parent'] = "Hoby Buchanon"
            item['site'] = "Hoby Buchanon"

            url = scene.xpath('.//div[@class="image_wrapper"]/a/@href').get()
            if url:
                item['url'] = url.strip()
                externid = re.search(r'.*/(.*?)/$', url).group(1)
                if externid:
                    item['id'] = externid.strip()

            title = scene.xpath('.//h2[@class="entry-title"]/a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = ''

            description = scene.xpath('.//div[@class="post-excerpt"]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())
            else:
                item['description'] = ''

            scenedate = scene.xpath('.//div[@class="date_label"]/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//div[@class="image_links double"]/a/@href').get()
            if not image:
                image = scene.xpath('.//div[@class="image_wrapper"]/a/img/@src').get()

            if image:
                item['image'] = image.strip()

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
                            scenelist.append(item.copy())
                    else:
                        scenelist.append(item.copy())
                item.clear()

        return scenelist
