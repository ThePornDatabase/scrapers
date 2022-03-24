import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class Spider(BaseSceneScraper):
    name = 'NastyCash'
    network = 'Nasty Cash'

    start_urls = [
        ['https://jolieandfriends.com', 'https://jolieandfriends.com/all-contents.c201.html?sort=date', 'Jolie and Friends'],
        ['https://altmodelbox.com', 'https://altmodelbox.com/lesbo.c64.html', 'Altmodelbox'],
        ['https://altmodelbox.com', 'https://altmodelbox.com/lesbo.c64.html', 'Altmodelbox'],
        ['https://altmodelbox.com', 'https://altmodelbox.com/sex-toys-games.c67.html', 'Altmodelbox'],
        ['https://teasingdolls.com', 'https://teasingdolls.com/11-en.html', 'Teasing Dolls'],
        ['https://amateurbestporn.com', 'https://amateurbestporn.com/all-videos.c7.html', 'Amateur Best Porn'],
        ['https://myasianslut.com', 'https://myasianslut.com/all-porn-asian-videos-teen-girl.html', 'My Asian Slut'],
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class, "video-desc")]/p/text()',
        'date': '//div[contains(@class, "content-extrainfo-box")]/span[contains(@class, "padding10")]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[@class="tags-wrapper"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/action/category-contents/201-%s?sort=date'
    }

    def start_requests(self):
        for link in self.start_urls:
            meta = {}
            meta['site'] = link[2]
            meta['parent'] = link[2]

            yield scrapy.Request(link[1], callback=self.get_scenes,
                                 headers=self.headers,
                                 cookies=self.cookies,
                                 meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "content-grid-box")]/a[@class="block"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "jolieandfriends" in response.url:
            tags.append('Trans')
        if "amateurbestporn" in response.url:
            tags.append('Amateur')
        if "myasianslut" in response.url:
            tags.append('Asian')
            tags.append('Amateur')
        return tags
