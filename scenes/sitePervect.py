import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePervectSpider(BaseSceneScraper):
    name = 'Pervect'
    site = 'Pervect'

    start_urls = [
        'https://pervect.com',
    ]

    selector_map = {
        'title': '//div[@class="container"]/h1/text()',
        'description': '//div[@class="container"]//div[contains(@class, "player-text")]//text()',
        'date': '//meta[@property="video:release_date"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Starring:")]/following-sibling::a/text()',
        'tags': '//ul[contains(@class,"player-tag-list")]/li/a/text()',
        'duration': '//meta[@property="video:duration"]/@content',
        'trailer': '//script[contains(text(), "contentUrl")]/text()',
        're_trailer': r'contentUrl.*?(http.*?\.mp4)',
        'external_id': r'.*/(.*?)/',
        'pagination': '/scenes/?mode=async&function=get_block&block_id=list_videos_latest_videos_list&sort_by=post_date&from=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"card-item")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: x.lower(), tags))
        changetags = [['ass2mouth', 'ATM'], ['bigbooty', 'Big Butt'], ['bigdildo', 'Dildo'], ['bigtits', 'Big Boobs'], ['sextoys', 'Toys']]
        for tag in changetags:
            if tag[0] in tags:
                tags.remove(tag[0])
                tags.append(tag[1])
        tags = list(map(lambda x: string.capwords(x), tags))
        return tags

