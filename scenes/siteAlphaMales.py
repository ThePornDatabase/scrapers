import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'alphamales-toolbox': 'Alpha Males Toolbox',
        'aplphamales-2-0': 'Alpha Males 2.0',
        'men-of-the-world': 'Men of the World',
        'blue-blake': 'Blue Blake',
        'hot-spunks-studios': 'Hot Spunk Studios'
    }
    return match.get(argument, argument)


class SiteAlphaMales(BaseSceneScraper):
    name = 'AlphaMales'
    network = 'Alpha Males'

    url = 'https://www.alphamales.com'

    paginations = [
        # ~ '/en/videos/alphamales/?page=%s',
        '/en/videos/alphamales-toolbox/?page=%s',
        '/en/videos/aplphamales-2-0/?page=%s',
        '/en/videos/men-of-the-world/?page=%s',
        '/en/videos/blue-blake/?page=%s',
        '/en/videos/hot-spunks-studios/?page=%s'
    ]

    selector_map = {
        'title': '//div[contains(@class, "col-12 text-center")]/h1/text()',
        'description': '//div[contains(@class, "col-12")]/h2/text()',
        'date': '',
        'image': '//div[contains(@class, "d-block embed-responsive embed-responsive-16by9 mb-2 rounded ")]/img/@src',
        'performers': '//i[contains(@class,"fa-star ")]/following-sibling::text()',
        'tags': '//div[contains(@class, "col-12 text-center px-4 py-2")]/a/h3/text()',
        'external_id': r'detail/(\d+)-',
        'trailer': '//video[contains(@class, "embed-responsive-item obj-cover d-none")]/source/@src',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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

    def get_next_page_url(self, url, page, pagination):
        page = str(int(page) - 1)
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"video-gallery")]/a[contains(@href, "en/videos/detail")][1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        meta = response.meta
        site = re.search(r'videos/(.*?)/', meta['pagination']).group(1)
        return match_site(site)

    def get_parent(self, response):
        meta = response.meta
        parent = re.search(r'videos/(.*?)/', meta['pagination']).group(1)
        return match_site(parent)

    def get_duration(self, response):
        duration = response.xpath('//span[@class="mx-1" and contains(text(), "Time")]/text()')
        if duration:
            duration = duration.get()
            duration = "".join(duration).replace("\n", "").replace("\t", "").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None
