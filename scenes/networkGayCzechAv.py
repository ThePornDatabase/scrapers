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
        'external_id': r'/video/(.+?)/',
        'trailer': '//script[contains(@type, "json")]/text()',
        're_trailer': r'contentUrl[\'\"]\s*:\s*[\'\"](https?://[^\'\"]+)',
        # Same rebuild as the CzechAv, GlaminoGirls and R51 sites: /pages/page-N/ is
        # gone and each site serves its whole listing on the root, with the cards
        # linking straight to /video/<slug>/.
        'pagination': ''
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
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
