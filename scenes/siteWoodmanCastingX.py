import re
import tldextract

import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class WoodmanCastingXScraper(BaseSceneScraper):
    name = 'WoodmanCastingX'
    network = 'Karak Ltd'
    parent = 'Woodman Casting X'

    start_urls = [
        'https://www.woodmancastingx.com',
    ]

    pagination = [
        '/casting-x/?page=%s',
        '/hardcore/?page=%s',
        '/backstage/?page=%s',
        '/sthuf/?page=%s',
        '/live/?page=%s'
    ]

    selector_map = {
        'title': '//div[@class="page_title"]/h1/text()',
        'description': '//p[@class="description"]/descendant-or-self::*/text()',
        'date': '//span[@class="label_info" and contains(text(), "Published")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//a[@class="girl_item"]/span/text()',
        'tags': '//div[contains(@class,"tags")]/a[@class="tag"]/text()',
        'external_id': r'.*/(.*).html',
        'trailer': '//script[contains(text(),"sources.push")]/text()',
        'pagination': '/casting-x/?page=%s'
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
        return self.format_url(
            base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class,"item scene")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = ''

        desc_row = self.process_xpath(
            response, self.get_selector_map('description')).getall()
        for desc in desc_row:
            if desc.strip():
                description = description + desc.strip() + '\n'

        return self.cleanup_description(description)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if re.search(r'\d{4}-\d{2}-\d{2}', date):
            date = re.search(r'(\d{4}-\d{2}-\d{2})', date).group(1)
        else:
            date = self.parse_date('today')

        return self.parse_date(date.strip()).isoformat()

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).getall()
        if performers:
            return list(map(lambda x: x.strip().title(), performers))
        return []

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search(r'url:\s+?\"(.*\.mp4.*?)\"', trailer).group(1)
                return trailer
        return ''

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return self.cleanup_title(title)
        return ''

    def get_site(self, response):
        pagination = response.meta['pagination']
        site = tldextract.extract(response.url).domain

        if 'casting-x' in pagination:
            return 'Woodman Casting X'
        if 'hardcore' in pagination:
            return 'Woodman Scenes XXXX'
        if 'backstage' in pagination:
            return 'Woodman Behind the Scene'
        if 'live' in pagination:
            return 'Woodman Live Cam Chat'
        if 'sthuf' in pagination:
            return 'Woodman Sthuf'

        return site

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.replace("_", "-").strip()
        return search
