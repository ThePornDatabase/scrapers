import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class networkManojobSpider(BaseSceneScraper):
    name = 'Manojob'
    network = 'Manojob'

    start_urls = [
        'https://manojob.com/',
    ]
    start_urls = [
        ['https://www.finishesthejob.com', '/updates/manojob/%s', 'Manojob'],
        ['https://www.finishesthejob.com', '/updates/mrpov/%s', 'Mister POV'],
        ['https://www.finishesthejob.com', '/updates/thedicksuckers/%s', 'The Dick Suckers'],

    ]
    
    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="row"]/div/div[@class="text-center"]/preceding-sibling::p[1]/text()',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//div[@class="video"]//video/@poster',
        'performers': '//h3[contains(text(),"Starring")]/a/text()',
        'tags': '//p[contains(text(),"Categories")]/a/text()',
        'external_id': '.*\/(.*)',
        'trailer': '//div[@class="video"]//video/source/@src',
        'pagination': '/updates/%s'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination':link[1], 'site':link[2], 'url':link[0]},
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
        scenes = response.xpath('//div[@class="card scene"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        meta = response.meta
        return meta['site']

    def get_parent(self, response):
        meta = response.meta
        return meta['site']

