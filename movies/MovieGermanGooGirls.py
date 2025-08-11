import re
import requests
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieGermanGooGirlsSpider(BaseSceneScraper):
    name = 'GermanGooGirls'
    network = 'German Goo Girls'
    parent = 'German Goo Girls'
    site = 'German Goo Girls'

    start_urls = [
        'https://www.ggg-german-bukkake.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//table[@class="description"]//p//text()',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//img[contains(@src, "moviecover")]/@src',
        'performers': '//td[contains(./strong/text(), "Starring:")]/a/text()',
        'tags': '//div[contains(@class, "meta-category")]//a[contains(@href, "/tag/")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Movie',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "post")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id').get()
            meta['id'] = re.search(r'-(\d+)', sceneid).group(1)
            scene = scene.xpath('./div[1]/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        performers = super().get_performers(response)

        tags2 = []
        for tag in tags:
            add_tag = True
            checktag = re.sub(r'[^a-z0-9]+', '', tag.lower())
            for perf in performers:
                checkperf = re.sub(r'[^a-z0-9]+', '', perf.lower())
                if checkperf in checktag:
                    add_tag = False
                if "ggg" in checkperf:
                    add_tag = False
            if add_tag:
                tags2.append(string.capwords(tag))
        return tags2
