import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkWeAreHairyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//meta[@itemprop="position" and @content="3"]/preceding-sibling::span/text()',
        'image': '//div[@class="lhs"]/img/@src',
        'height': '//p[@id="height_both"]/text()',
        'weight': '//p[@id="weight_both"]/text()',
        'cupsize': '//h3[contains(text(), "Bust Size")]/following-sibling::p/text()',
        'pagination': '/models/page%s.shtml',
        'external_id': r'models/(.*).html'
    }

    name = 'WeAreHairyPerformer'
    network = "We Are Hairy"

    start_urls = [
        'https://www.wearehairy.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="mtb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d{3})', height)
        if height:
            height = height.group(1) + "cm"
        return height

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'(\d{2,3})', weight)
        if weight:
            weight = weight.group(1) + "kg"
        return weight
