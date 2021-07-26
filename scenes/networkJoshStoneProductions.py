import scrapy
import re
import dateparser
import string
import html
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


class networkJoshStoneProductionsSpider(BaseSceneScraper):
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
        'external_id': '.*\/(.*?).html',
        'trailer': '//video/source/@src',
        'pagination': '/tour3/category.php?id=5&page=%s&s=d'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[contains(@class,"pad_bottom_15 text-center")]')
        for scene in scenes:
            title = scene.xpath('./h3/a/text()').get()
            if title:
                meta['title'] = html.unescape(string.capwords(title.strip()))

            date = scene.xpath('./p[1]/text()').get()
            if date:
                meta['date'] = dateparser.parse(date, date_formats=['%B %d, %Y']).isoformat()
            else:
                meta['date'] = dateparser.parse(today()).isoformat()

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
        else:
            return tldextract.extract(response.url).domain
        
    def get_parent(self, response):
        parent = response.xpath('//p[@class="pull-right"]/b/text()').get()
        if parent:
            return parent.strip()
        else:
            return tldextract.extract(response.url).domain

    def get_tags(self, response):
        return ['Transsexual', 'Transgender']

    def get_id(self, response):
        if 'external_id' in self.regex and self.regex['external_id']:
            search = self.regex['external_id'].search(response.url)
            if search:
                return search.group(1).lower()

        return None
