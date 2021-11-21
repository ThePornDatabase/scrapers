import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkJoshStoneProductionsSpider(BaseSceneScraper):
    name = 'JoshStoneProductions'
    network = 'Josh Stone Productions'

    start_urls = [
        'https://www.trans500.com/',
    ]

    selector_map = {
        'title': '//h2[1]/text()',
        'description': '//p[@class="description"]/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '',
        'tags': '//li[contains(@class,"tag")]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//video/source/@src',
        'pagination': '/tour3/category.php?id=5&page=%s&s=d'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[contains(@class,"pad_bottom_15 text-center")]')
        for scene in scenes:
            title = scene.xpath('./h3/a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)

            date = scene.xpath('./p[1]/text()').get()
            if date:
                meta['date'] = self.parse_date(date, date_formats=['%B %d, %Y']).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('./p[contains(@class,"categories")]/a/text()').getall()
            if performers:
                meta['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                meta['performers'] = []

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//p[@class="pull-right"]/b/text()').get()
        if site:
            return site.strip()
        return tldextract.extract(response.url).domain

    def get_parent(self, response):
        parent = response.xpath('//p[@class="pull-right"]/b/text()').get()
        if parent:
            return parent.strip()
        return tldextract.extract(response.url).domain

    def get_tags(self, response):
        return ['Transsexual', 'Transgender']

    def get_id(self, response):
        return super().get_id(response).lower()
