import re
import scrapy
import string

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLilDsPlayhouseSpider(BaseSceneScraper):
    name = 'LilDsPlayhouse'
    network = 'Radical Entertainment'
    parent = 'Lil Ds Playhouse'
    site = 'Lil Ds Playhouse'

    start_urls = [
        'https://lildsplayhouse.com',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//p[@class="description"]//text()',
        'date': '//i[@class="fa fa-circle"]/following-sibling::span[not(contains(text(), ":"))]/text()',
        'image': '//meta[@property="og:image"]/@content',
        're_image': r'(http.*\.jpg)',
        'performers': '//div[@class="model-lists"]/a/text()',
        'duration': '//i[@class="fa fa-circle"]/following-sibling::span[contains(text(), ":")]/text()',
        'tags': '//div[contains(@class,"content-tags")]//a/text()',
        'external_id': r'.*/(.*?)$',
        'trailer': '//div[@class="player-wrap"]//video/source/@src',
        'pagination': '/videos?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-card-info"]/div[1]/div[1]//a[contains(@href, "/videos/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "Radical Entertainment"
            performer_extra['site'] = "Lil Ds Playhouse"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data
