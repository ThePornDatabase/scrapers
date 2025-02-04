import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkBrokeStraightboysPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'image': '//img[contains(@src, "thumbs") and contains(@src, "models")]/@src',
        'image_blob': True,
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()|//li[contains(text(), "Height")]/strong/text()',
        're_height': r'(\d+)cm',
        'weight': '//strong[contains(text(), "Weight")]/following-sibling::text()|//li[contains(text(), "Weight")]/strong/text()',

        'pagination': '/models.php?page=%s&s=1&nats=',
        'external_id': r'model/(.*)/'
    }

    name = 'BrokeStraightboysPerformer'
    network = 'Broke Straight Boys'

    start_urls = [
        'https://www.boygusher.com',
        'https://www.brokestraightboys.com',
        'https://www.collegeboyphysicals.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="tnTle"]/a|//div[@class="model-ebox"]/span/a')
        for performer in performers:
            meta['name'] = performer.xpath('./text()|./div/text()').get()
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta, cookies=self.cookies, headers=self.headers)

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'^(\d+)', weight)
        if weight:
            weight = weight.group(1)
            weight = str(int(int(weight) * .453592))
            return weight
        return None
