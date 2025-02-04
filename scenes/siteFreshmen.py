import re
import scrapy
from requests import get
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFreshmenSpider(BaseSceneScraper):
    name = 'Freshmen'
    site = 'Freshmen'
    parent = 'Freshmen'
    network = 'Freshmen'

    start_urls = [
        'https://www.freshmen.net'
    ]

    selector_map = {
        'description': '//h1/following-sibling::p[1]/text()',
        'image': '//video/@poster|//div[@class="big_photo"]/img/@src',
        'performers': '//div[@class="actor"]/a/following-sibling::div/text()',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/archive?case=loadmore&id=%s',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        link = "https://www.freshmen.net/archive"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        scenelist = response.xpath('//div[@class="issue_item"]/@data-issue').getall()
        scenelist.sort(reverse=True)
        yield scrapy.Request(url=self.get_next_page_url(response.url, scenelist[0]), callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        scenelist = response.xpath('//div[@class="issue_item"]/@data-issue').getall()
        scenelist.sort()
        sceneid = scenelist[0]

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, sceneid), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="issue_item"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-issue').get()
            title = scene.xpath('.//h2//text()').getall()
            title = " ".join(title)
            meta['title'] = self.cleanup_title(title)
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay']

    def get_duration(self, response):
        duration = response.xpath('//span[@class="addspecs"]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None
