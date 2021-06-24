import scrapy
import re
import datetime
import dateparser

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
        'external_id': '.*\/(.*?)\/$',
        'trailer': '', #trailer is on site, but hosted through a third party with tokens
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
        return self.format_url(
            base, pagination % page)                                     

    def get_scenes(self, response):
        SceneList = []
        scenes = response.xpath('//div[contains(@class,"post-item")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['image'] = ''
            item['description'] = ''
            item['network'] = "Hoby Buchanon"
            item['parent'] = "Hoby Buchanon"
            item['site'] = "Hoby Buchanon"
            
            url = scene.xpath('.//div[@class="image_wrapper"]/a/@href').get()
            if url:
                item['url'] = url.strip()
                id = re.search('.*\/(.*?)\/$', url).group(1)
                if id:
                    item['id'] = id.strip()

            
            title = scene.xpath('.//h2[@class="entry-title"]/a/text()').get()
            if title:
                item['title'] = title.strip()
            
            description = scene.xpath('.//div[@class="post-excerpt"]/text()').get()
            if description:
                item['description'] = description.strip()
            
            date = scene.xpath('.//div[@class="date_label"]/text()').get()
            if date:
                item['date'] = dateparser.parse(date.strip()).isoformat()
            
            image = scene.xpath('.//div[@class="image_links double"]/a/@href').get()
            if not image:
                image = scene.xpath('.//div[@class="image_wrapper"]/a/img/@src').get()
                
            if image:
                item['image'] = image.strip()

            if item['id'] and item['title'] and item['date']:
                SceneList.append(item.copy())
                item.clear()
                
        return SceneList
            
            


