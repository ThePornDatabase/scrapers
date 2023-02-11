import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTreasureIslandMediaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model-profile")]/h3[1]/text()',
        'image': '//div[contains(@class, "model-profile")]/div[1]//a[1]/img/@src',
        'ethnicity': '//li[contains(@class, "list-group-item") and contains(text()[2], "thnicity")]/span/text()',
        'eyecolor': '//li[contains(@class, "list-group-item") and contains(text()[2], "Eye")]/span/text()',
        'haircolor': '//li[contains(@class, "list-group-item") and contains(text()[2], "Hair")]/span/text()',
        'height': '//li[contains(@class, "list-group-item") and contains(text()[2], "Height")]/span/text()',
        'weight': '//li[contains(@class, "list-group-item") and contains(text()[2], "Weight")]/span/text()',

        'pagination': '/men?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'TreasureIslandMediaPerformer'
    network = 'Treasure Island Media'

    start_urls = [
        'https://ghr.treasureislandmedia.com',
        'https://timfuck.treasureislandmedia.com',
        'https://timsuck.treasureislandmedia.com',
        'https://timjack.treasureislandmedia.com',
        'https://latinloads.treasureislandmedia.com',
        'https://bruthaload.treasureislandmedia.com',
        'https://knockedoutjerkedoff.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "page-scene-wrap")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
