import re
from datetime import date, timedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSocialGlamourSpider(BaseSceneScraper):
    name = 'SocialGlamour'
    network = 'Social Glamour'
    max_pages = 20

    start_urls = [
        'https://www.socialglamour.com'
    ]

    pagination = [
        '/categories/tease_%s_d.html',
        '/categories/behind-the-scenes_%s_d.html',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'performers': '',
        'date': '',
        'image': '',
        'tags': '',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/categories/tease_%s_d.html'
    }

    def start_requests(self):
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
        scenes = response.xpath('//div[@class="product-item"]')
        if response.meta['page'] < self.max_pages:
            for scene in scenes:
                item = SceneItem()
                title = scene.xpath('./h3/a/text()').get()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''

                item['description'] = ''

                performers = scene.xpath('.//div[@class="pi-model"]//span/a/text()')
                if performers:
                    performers = performers.getall()
                    item['performers'] = list(map(lambda x: x.strip(), performers))
                else:
                    item['performers'] = []

                date_xpath = scene.xpath('..//i[contains(@class, "fa-calendar")]/following-sibling::text()')
                item['date'] = self.parse_date('today').isoformat()
                if date_xpath:
                    date_xpath = date_xpath.get().strip()
                    item['date'] = self.parse_date(date_xpath, date_formats=['%Y-%m-%d']).isoformat()

                image = scene.xpath('./div/a/img/@src')
                if image:
                    image = image.get()
                    item['image'] = image.strip()
                else:
                    item['image'] = None

                item['image_blob'] = None

                item['tags'] = []
                if "behind-the-scenes" in response.url:
                    item['tags'].append('BTS')
                item['trailer'] = ''
                item['site'] = "Social Glamour"
                item['parent'] = "Social Glamour"
                item['network'] = "Social Glamour"

                item['url'] = scene.xpath('./div/a/@href').get()
                if "signup" in item['url']:
                    item['url'] = response.url

                extern_id = re.search(r'.*/(.*?)\.jpg', item['image'])
                if extern_id:
                    item['id'] = extern_id.group(1).lower().strip()

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
