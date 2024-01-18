import re
import html
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKinkAcademySpider(BaseSceneScraper):
    name = 'KinkAcademy'
    network = 'Kink Academy'
    parent = 'Kink Academy'
    site = 'Kink Academy'

    start_url = 'https://www.kinkacademy.com'

    paginations = [
        '/category/skill-level/basic-skill/page/%s/',
        '/category/skill-level/intermediate-skill/page/%s/',
        '/category/skill-level/advanced-skill/page/%s/',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//figure[@class="featured-image"]/../following-sibling::p[1]/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//figure[@class="featured-image"]/img/@src',
        'performers': '',
        'tags': '//p[@class="entry-meta"]/span[@class="categories"]/span[@class="terms"]/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            link = 'https://www.kinkacademy.com'
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[contains(@class, "format-video")]/header/figure/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performerlist = response.xpath('//span[@class="post-instructors"]/span[@class="terms"]/a/text()')
        if performerlist:
            performerlist = performerlist.getall()
        performers = []
        for perf in performerlist:
            performers.append(string.capwords(html.unescape(perf)))
        return performers
