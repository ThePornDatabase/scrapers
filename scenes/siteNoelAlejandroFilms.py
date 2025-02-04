import re
import string
import scrapy
from requests import get
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNoelAlejandroFilmsSpider(BaseSceneScraper):
    name = 'NoelAlejandroFilms'
    network = 'Noel Alejandro Films'
    parent = 'Noel Alejandro Films'
    site = 'Noel Alejandro Films'

    start_urls = [
        'https://www.noelalejandrofilms.com/films/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"film-prologue")]//text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'date_published.*?(\d{4}-\d{2}-\d{2})',
        'image': '//video/@poster',
        'director': '//span[contains(text(), "Director")]/following-sibling::text()',
        'performers': '//span[contains(@class, "casting")]/following-sibling::a/text()',
        'tags': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "product")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        scenedate = response.xpath('//span[contains(text(), "Year")]/following-sibling::text()')
        if scenedate:
            scenedate = re.search(r'(\d{4})', scenedate.get()).group(1)
            return scenedate + "-01-01"
        return ""

    def get_duration(self, response):
        duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_tags(self, response):
        return ['Gay']

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Noel Alejandro Films"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
