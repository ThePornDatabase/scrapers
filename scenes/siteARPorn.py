import re
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRPornSpider(BaseSceneScraper):
    name = 'ARPorn'

    start_url = "https://vrporn.com"

    start_urls = [
        ['/studio/arporn/page/%s/?sort=newest', 'AR Porn'],
        ['/studio/vrfanservice/page/%s/?sort=newest', 'VR Fan Service'],
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"ui-detail-video__content-inner")]//text()',
        'date': '//script[contains(@type,"ld+json")]/text()',
        're_date': r'uploadDate[\'\"].*?[\'\"](.*?)[\'\"],',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class,"ui-card-model__content")]/a/text()',
        'tags': '//h3[contains(text(), "Tags")]//following-sibling::div[1]/a[contains(@href, "/tag/")]/text()',
        'duration': '//script[contains(@type,"ld+json")]/text()',
        're_duration': r'duration[\'\"].*?[\'\"](.*?)[\'\"],',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for site in self.start_urls:
            meta['pagination'] = site[0]
            meta['site'] = site[1]
            meta['parent'] = site[1]
            meta['network'] = site[1]
            url = url=self.get_next_page_url(self.start_url, meta['page'], meta['pagination'])
            yield scrapy.Request(url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies, dont_filter=True)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, dont_filter=True)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta, dont_filter=True)

    def get_date(self, response):
        scenedate = response.xpath('//script[contains(@type,"ld+json")]/text()').get()
        scenedate = scenedate.replace("\r", "").replace("\n", "").replace("\t", "").replace("", "")
        scenedate = re.search(r'uploadDate[\'\"].*?[\'\"](\d{4}-\d{2}-\d{2}).*?[\'\"],', scenedate)
        if scenedate:
            return scenedate.group(1)
        return None

    def get_duration(self, response):
        duration = super().get_duration(response)
        try:
            duration = str(int(duration))
        except:
            duration = ""
        return duration
