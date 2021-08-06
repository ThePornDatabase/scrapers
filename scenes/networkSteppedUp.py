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
        'title': '//*[@class="title"]/text()',
        'description': '//div[contains(@class, "desc")]/p/text()',
        'date': '//div[@class="content-page-info"]//span[@class="post-date"]/text() | //div[@class="content-meta"]//span[contains(@class, "date")]/text()',
        'performers': '//div[@class="content-meta-wrap"]//h4[@class="models"]/a/text()',
        'tags': '',
        'trailer': '//video/source/@src',
        'external_id': r'view/([^/]+)',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "thumb-full")] | //div[@class="content-border"]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()

            if re.search(self.get_selector_map('external_id'), link) is not None:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene)

    def get_image(self, response):
        xpaths = [
            '//div[@id="trailer-player"]/@data-screencap',
            '//video[contains(@id, "ypp-player")]/@poster',
            '//a[@href="%s"]//img/@src' % response.url,
            '//div[@class="view-thumbs"]//img/@src',
            '//a//img[@src]/@src'
        ]

        for xpath in xpaths:
            image = response.xpath(xpath)
            if image is not None:
                image = image.get()
                if image is not None:
                    return image

        return None
