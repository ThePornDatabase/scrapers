import json
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class TeenCoreClubPerformerSpider(BasePerformerScraper):
    name = 'TeenCoreClubPerformer'
    network = 'Teen Core Club'
    parent = 'Teen Core Club'

    start_urls = [
        ['https://www.teencoreclub.com', 'https://www.teencoreclub.com/api/actors?page=%s'],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'updates/(.*)\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0
        print(f'Response: {response.url}')
        performers = self.parse_performerpage(response)
        if performers:
            count = len(performers)
            for performer in performers:
                yield performer

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

    def parse_performerpage(self, response):
        global json
        itemlist = []

        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            item = PerformerItem()

            item['name'] = jsonentry['name'].title().strip()
            item['network'] = 'Teen Core Club'
            item['url'] = "https://www.teencoreclub.com/browsevideos/actor/" + str(jsonentry['id']) + "/" + jsonentry['name'].replace(" ", "%20").strip()
            item['image'] = "https://www.teencoreclub.com" + jsonentry['image'].replace("\\", "").strip()
            item['image_blob'] = None
            item['bio'] = jsonentry['bio']
            if not item['bio']:
                item['bio'] = ''

            item['gender'] = "Female"
            item['birthday'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['nationality'] = ''
            item['haircolor'] = ''
            item['weight'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['cupsize'] = ''
            item['fakeboobs'] = ''
            item['eyecolor'] = ''

            itemlist.append(item.copy())
            item.clear()

        return itemlist
