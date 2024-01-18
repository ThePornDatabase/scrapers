import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'amateurgaypov': 'Amateur Gay POV',
        'broseekingbro': 'Bro Seeking Bro',
        'casual-dudes': 'Casual Dudes',
        'hotafmen': 'Hot AF Men',
        'masqulin': 'Masqulin',
        'men-of-montreal': 'Men Of Montreal',
    }
    return match.get(argument.lower(), argument)


class NetworkBroNetworkSpider(BaseSceneScraper):
    name = 'BroNetwork'
    network = 'Bro Network'

    start_url = 'https://thebronetwork.com'

    paginations = [
        '/categories/amateurgaypov_%s_d.html',
        '/categories/broseekingbro_%s_d.html',
        '/categories/casual-dudes_%s_d.html',
        '/categories/hotafmen_%s_d.html',
        '/categories/masqulin_%s_d.html',
        '/categories/men-of-montreal_%s_d.html',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//p[@class="update_description"]/text()',
        'date': '//div[contains(@class,"gallery_info")]/p/span[@class="availdate"][1]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//video-js/@poster',
        'performers': '//div[contains(@class,"gallery_info")]//span[@class="tour_update_models"]/a/text()',
        'tags': '//a[@class="tagsVideoPage"]/text()',
        'duration': '//div[contains(@class,"gallery_info")]/p/span[@class="availdate"][2]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//div[@class="fullscreenTour"]//source/@src',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
        scenes = response.xpath('//div[@class="updateDetails"]')
        for scene in scenes:
            sceneid = scene.xpath('.//img/@id').get()
            meta['id'] = re.search(r'target-(\d+)', sceneid).group(1)
            scene = scene.xpath('./a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        match_text = re.search(r'.*/(.*?)_', response.meta['pagination']).group(1)
        site = match_site(match_text)
        if site == match_site:
            site = "Bro Network"
        return site

    def get_parent(self, response):
        match_text = re.search(r'.*/(.*?)_', response.meta['pagination']).group(1)
        parent = match_site(match_text)
        if parent == match_site:
            parent = "Bro Network"
        return parent
