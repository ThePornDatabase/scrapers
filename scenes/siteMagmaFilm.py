import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class MagmaFilmNetworkSpider(BaseSceneScraper):
    name = 'MagmaFilm'

    start_urls = [
        'http://www.magmafilm.tv',
    ]

    cookies = {
        '_culture': 'en',
    }

    selector_map = {
        'title': 'h2:first-of-type::text',
        'description': '//div[@class="infobox"]/div/p/text()',
        'date': '',
        'image': '//div[contains(@class, "imgbox") and contains(@class, "full")]/@style',
        're_image': r'url\(\'(.*)\'\)',
        'performers': '//div[@class="infobox"]/div/table//td/div/text()',
        'tags': '//div[@class="infobox"]/div/table//td/a/span/text()',
        'external_id': r'/([a-zA-Z0-9-]+?)/?$',
        'trailer': '',
        'pagination': '/en/List/Neu?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "clipbox")]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
