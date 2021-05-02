import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CherryPimpsSpider(BaseSceneScraper):
    name = 'CherryPimps'
    network = 'cherrypimps'

    start_urls = [
        'https://www.cherrypimps.com'
    ]

    selector_map = {
        'title': '//*[@class="trailer-block_title"]/text() | //h1/text()',
        'description': '//div[@class="info-block"]//p[@class="text"]/text() | //div[@class="update-info-block"]//p/text()',
        'image': '//img[contains(@class, "update_thumb")]/@src | //img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '//div[contains(@class, "model-list-item")]//a/span/text()',
        'tags': "ul.tags a::text",
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
        'pagination': '/categories/movies_%s.html'
    }

    def get_scenes(self, response):
        """ Returns a list of scenes
        @url https://cherrypimps.com/categories/movies.html
        @returns requests 10 50
        """
        scenes = response.css("div.item-updates .item-thumb a::attr(href)").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_date(self, response):
        selector = '//div[@class="info-block_data"]//p[@class="text"]/text() | //div[@class="update-info-row"]/text()'
        date = response.xpath(selector).extract()[1]
        date = date.split('|')[0].replace('Added', '').replace(':', '').strip()
        return dateparser.parse(date).isoformat()

    def get_site(self, response):
        return response.css('.series-item-logo::attr(title)').get().strip()
