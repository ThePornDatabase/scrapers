import re
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRPornSpider(BaseSceneScraper):
    name = 'ARPorn'

    start_urls = [
        ['https://vrporn.com/studio/arporn/', 'AR Porn'],
        ['https://vrporn.com/studio/vrfanservice/', 'VR Fan Service'],
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//script[contains(@type,"ld+json")]/text()',
        're_description': r'description[\'\"].*?[\'\"](.*?)[\'\"],',
        'date': '//script[contains(@type,"ld+json")]/text()',
        're_date': r'uploadDate[\'\"].*?[\'\"](.*?)[\'\"],',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h3[contains(text(), "Starring")]/following-sibling::div[1]//div[@class="name_pornstar"]/text()',
        'tags': '//h3[contains(text(), "Tags")]/../following-sibling::div[1]/a/text()',
        'duration': '//script[contains(@type,"ld+json")]/text()',
        're_duration': r'duration[\'\"].*?[\'\"](.*?)[\'\"],',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for site in self.start_urls:
            link = site[0]
            meta['site'] = site[1]
            meta['parent'] = site[1]
            meta['network'] = site[1]
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@title, "Video Thumbnail")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        scenedate = response.xpath('//script[contains(@type,"ld+json")]/text()').get()
        scenedate = scenedate.replace("\r", "").replace("\n", "").replace("\t", "").replace("", "")
        scenedate = re.search(r'uploadDate[\'\"].*?[\'\"](\d{4}-\d{2}-\d{2}).*?[\'\"],', scenedate)
        if scenedate:
            return scenedate.group(1)
        return None
