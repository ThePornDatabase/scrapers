import re
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePeepshowTVSpider(BaseSceneScraper):
    name = 'PeepshowTV'
    site = 'PeepshowTV'
    parent = 'PeepshowTV'
    network = 'PeepshowTV'

    start_urls = [
        'https://www.peepshow.tv'
    ]

    selector_map = {
        'title': '//div[@class="videoinfo"]/div[1]/p/text()',
        'description': '//div[@class="videoinfo"]/div/p/strong[contains(./font, "Description")]/following-sibling::text()',
        'date': '//div[@class="videoinfo"]/div[contains(text(), "Added")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="carousel-inner"]/div[1]/img[1]/@src',
        'performers': '',
        'tags': '//div[@class="videoinfo"]/div/p/strong[contains(./font, "Keywords")]/following-sibling::a/text()',
        'type': 'Scene',
        'external_id': r'lid=(\d+)',
        'pagination': '/show.php?a=119_%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="itemv"]/a/@href').getall()
        for scene in scenes:
            meta['id'] = re.search(r'lid=(\d+)', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        return html.unescape(title)

    def get_performers(self, response):
        performers = []
        title = self.get_title(response)
        performer = re.search(r'(.*?) -', title)
        if performer:
            performer = performer.group(1)
            performers = performer.split("&")
            performers = list(map(lambda x: self.cleanup_title(x.strip()), performers))
        return performers

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "PeepshowTV"
                perf['site'] = "PeepshowTV"
                performers_data.append(perf)
        return performers_data

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            temptag = re.search(r' - (.*)', tag)
            if temptag:
                tags2.append(temptag.group(1))
            else:
                tags2.append(tag)
        return tags2
