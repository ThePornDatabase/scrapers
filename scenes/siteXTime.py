import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        '01': 'XTime Premiere',
        '02': 'XTime Bluebird',
        '03': 'XTime Eros Art',
        '04': 'XTime Lethal Hardcore',
        '05': 'XTime Filly Films',
        '06': 'XTime Samurai',
        '08': 'XTime Lady Boy',
        '09': 'XTime Combat-Zone',
        '10': 'XTime Alexander DeVoe',
        '11': 'XTime Mercenary Pictures',
        '12': 'XTime Nacho Vidal',
        '13': 'XTime Omar Galanti',
        '14': 'XTime Diva Del Turbo',
        '15': 'XTime Live Sofia',
        '16': 'XTime Woodman Production',
        '17': 'XTime International Star',
        '18': 'XTime Young Sinner',
        '19': 'XTime MILF Parade',
        '20': 'XTime Black Desire',
        '21': 'XTime Cuckold',
        '22': 'XTime Big Tits',
        '23': 'XTime Nasty Senior',
        '24': 'XTime Grandi Film HD',
        '25': 'XTime Famiglie Italiane',
        '26': 'XTime El Matador',
        '27': 'XTime Jessica Rizzo',
        '28': 'XTime Download Channel',
        '43': 'XTime Great Classics',
    }
    return match.get(argument, "XTime")


class SiteXTimeSpider(BaseSceneScraper):
    name = 'XTime'
    network = 'XTime'

    start_urls = [
        'http://xtime.tv',
    ]

    selector_map = {
        'title': '//h1/div/text()',
        'description': '',
        'date': '//li[contains(text(), "Published")]/span/text()',
        'image': '//script[contains(text(), "immaggini")]/text()',
        're_image': r'Array.*?\(\'(.*?\.jpg)',
        'performers': '//div[@id="div-dettagli-cast"]/text()',
        'tags': '//div[@id="div-dettagli-categorie"]/text()',
        'external_id': r'trailer/(\d+)/',
        'trailer': '',
        'pagination': '/?act=Scenes&pageID=%s&order=data_pubblicazione&datapub=anno'
    }

    def start_requests(self):
        link = "http://xtime.tv/?act=Disclaimer&accept=1"
        yield scrapy.Request(link, callback=self.start_requests_2,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests_2(self, response):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//ul[@class="item"]/li/table//tr/td/a[contains(@href, "/trailer")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//a[@class="video-label-canale"]/@href')
        if site:
            site = site.get()
            if re.search(r'canali/.*?(\d+).*?/', site):
                site = re.search(r'canali/.*?(\d+).*?/', site).group(1)
            else:
                site = 'XTime'
        return match_site(site)

    def get_parent(self, response):
        parent = response.xpath('//a[@class="video-label-canale"]/@href')
        if parent:
            parent = parent.get()
            if re.search(r'canali/.*?(\d+).*?/', parent):
                parent = re.search(r'canali/.*?(\d+).*?/', parent).group(1)
            else:
                parent = 'XTime'

        return match_site(parent)
