import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkKinkBombSpider(BaseSceneScraper):
    name = 'KinkBomb'
    network = 'KinkBomb'
    parent = 'KinkBomb'
    site = 'KinkBomb'

    start_urls = [
        'http://www.kinkbomb.com',
    ]

    selector_map = {
        'title': '//h1[@class="productviewtitle"]/text()',
        'description': '//div[@class="description-inner"]/p/text()',
        'date': '//span[contains(text(), "Posted:")]/following-sibling::text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="clip-preview-inner"]/video/@poster',
        'image_blob': True,
        'performers': '',
        'tags': '//span[contains(text(), "categories")]/following-sibling::a/text()|//span[contains(text(), "Category")]/following-sibling::a/text()',
        'external_id': r'.*/(\d+)',
        'trailer': '//div[@class="clip-preview-inner"]/video/source/@src',
        'pagination': '/all?sort=age&page=%s'
    }

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if self.limit_pages < 100:
                kb_max_pages = self.limit_pages * 25
            else:
                kb_max_pages = self.limit_pages
            if 'page' in response.meta and response.meta['page'] < kb_max_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item card"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = super().get_title(response)
        site = response.xpath('//h4[@class="studio-header-name"]/text()')
        if site:
            site = site.get()
            title = string.capwords(site.strip()) + ": " + title
        return title

    def get_image(self, response):
        image = super().get_image(response)
        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if not image:
                image = response.xpath('//div[@class="clip-preview-inner"]/video/@poster')
            if image:
                image = self.format_link(response, image.get())
            else:
                image = ''
        return image
