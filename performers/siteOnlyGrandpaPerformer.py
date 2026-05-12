import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model-profile")]//ancestor::div[contains(@class, "container")]//h2/text()',
        'image': '//div[contains(@class, "model-profile-thumb")]/img/@src',
        'image_blob': True,
        'bio': '//div[contains(@class, "model-profile")]//ancestor::div[contains(@class, "container")]//div[contains(@class, "section-text-content")]/p//text()',
        'haircolor': '//strong[contains(text(), "Hair Color:")]/following-sibling::text()',
        'nationality': '//strong[contains(text(), "Nationality:")]/following-sibling::text()',
        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'OnlyGrandpaPerformer'
    network = 'Only Grandpa'

    start_urls = [
        'https://onlygrandpa.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-model-thumb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
