import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkGayCzechAvSpider(BaseSceneScraper):
    name = 'GayCzechAv'
    network = 'Gay Czech AV'
    parent = 'Gay Czech AV'

    start_urls = [
        'https://czechgayamateurs.com',
        'https://czechgaycasting.com', #
        'https://czechgaycouples.com',
        'https://czechgayfantasy.com', #
        'https://czechgaymassage.com',
        'https://czechgaysolarium.com', #
    ]

    selector_map = {
        'title': '//script[contains(@type, "ld+json")]/text()',
        're_title': r'[\'\"]name[\'\"]\:\s+?[\'\"](.*?)[\'\"]',
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'uploadDate[\'\"].*?(\d{4}-\d{2}-\d{2})',
        'description': '//script[contains(@type, "json")]/text()',
        're_description': r'description[\'\"].*?[\'\"](.*?)[\'\"]',
        'duration': '//script[contains(@type, "json")]/text()',
        're_duration': r'duration[\'\"].*?[\'\"](.*?)[\'\"]',
        'image': "//meta[@property='og:image']/@content",
        'tags': "",
        'external_id': '.*/(.*?)/',
        'trailer': '',
        'pagination': '/pages/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"gap--150")]//h3/ancestor::a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath('//script[contains(@type, "json")]/text()')
        if tags:
            tags = re.search(r'keywords[\'\"].*?[\'\"](.*?)[\'\"]', tags.get())
            if tags:
                tags = tags.group(1)
                tags = tags.split(",")
                tags = list(map(lambda x: string.capwords(x.strip()), tags))
            tags2 = []
            for tag in tags:
                tag = re.sub(r'[^a-z]+', '', tag.lower())
                if tag:
                    tags2.append(tag)
        return tags2
