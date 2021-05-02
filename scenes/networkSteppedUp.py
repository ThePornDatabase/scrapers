import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SteppedUpSpider(BaseSceneScraper):
    name = 'SteppedUp'
    network = 'Stepped Up'

    start_urls = [
        'https://tour.swallowed.com',
        'https://tour.nympho.com',
        'https://tour.trueanal.com',
        'https://tour.allanal.com',
        'https://tour.analonly.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text() | //h2[@class="title"]/text()',
        'description': '//div[contains(@class, "desc")]/p/text() | //div[contains(@class, "content-description")]/p/text()',
        'date': "//div[@class='content-page-info']/div[@class='content-meta-wrap']/div[@class='content-meta']/p/span[@class='post-date']/text() | //div[@class='content-meta']//span[contains(@class,'date')]/text()",
        'performers': "//div[@class='content-meta-wrap']/div[@class='content-meta']/h4[@class='models']/a/text()",
        'tags': "",
        'trailer': '//video/source/@src',
        'external_id': 'view/([^/]+)',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "thumb-full")] | //div[@class="content-border"]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {
                'image': scene.css('a img::attr(src)').get()
            }

            if re.search(self.get_selector_map('external_id'), link) is not None:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        xpaths = [
            '//div[@id="trailer-player"]/@data-screencap',
            '//video[contains(@id, "ypp-player")]/@poster',
            '//a[@href="%s"]//img/@src' % response.url,
            '//div[@class="view-thumbs"]//img/@src',
        ]

        for xpath in xpaths:
            if response.xpath(xpath) is not None:
                return response.xpath(xpath).get()
