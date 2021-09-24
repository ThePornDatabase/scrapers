import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class BangBrosAltSpider(BaseSceneScraper):
    name = 'BangBrosAlt'
    network = 'BangBros'

    start_urls = [
        'http://xxxpawn.com',
        'http://blackpatrol.com',
        'http://blacksonmoms.com',
        'https://filthyfamily.com',
    ]

    selector_map = {
        'title': '//span[@class="vdetitle"]/text() | //h1/text()',
        'description': '//span[@class="vdtx"] | //p[@class="videoDetail"]/text()',
        'external_id': '(video\\d+)/.+',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.css("a::attr(href)").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return re.search("var siteName = '(.+)'", response.text).group(1)

    def get_image(self, response):
        image = re.search("var playerImg = '(.+)'", response.text).group(1)
        image = image.replace('////', '//')
        if image.startswith('//'):
            image = 'http:' + image

        return image

    def get_trailer(self, response):
        trailer = re.search("var videoLink = '(.+)'", response.text).group(1)
        trailer = trailer.replace('////', 'http://')
        if trailer.startswith('//'):
            trailer = 'http:' + trailer
        return trailer

    def get_tags(self, response):
        tags = []
        genres = response.xpath(
            '//meta[@http-equiv="keywords"]/@content').get().split(',')
        for genrelink in genres:
            tags.append(genrelink.strip())

        return tags

    def get_date(self, response):
        return dateparser.parse('today').isoformat()

    def get_performers(self, response):
        return ['Unknown']

    def get_next_page_url(self, base, page):
        if 'xxxpawn' in base or 'blackpatrol' in base:
            return self.format_url(base, '/home/%s' % page)

        return self.format_url(base, '/videos/%s' % page)
