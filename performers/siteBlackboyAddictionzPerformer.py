import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBlackboyAddictionzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3/text()',
        'bio': '//h3/following-sibling::p[not(normalize-space(@class))]//text()',
        'astrology': '//ul/li[contains(text(), "Sign")]/strong/text()',
        'height': '//ul/li[contains(text(), "Height")]/strong/text()',
        'weight': '//ul/li[contains(text(), "Weight")]/strong/text()',
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BlackboyAddictionzPerformer'
    network = 'Blackboy Addictionz'
    site = 'Blackboy Addictionz'

    start_urls = [
        'https://www.blackboyaddictionz.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        meta = {}
        performers = response.xpath('//figure')
        for performer in performers:
            image = performer.xpath('.//img/@src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            perf_url = performer.xpath('./a/@href').get()
            yield scrapy.Request(url=self.format_link(response, perf_url), callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_height(self, response):
        height = super().get_height(response)
        if "'" in height:
            height = re.sub(r'[^0-9\']', '', height)
            feet = re.search(r'(\d+)\'', height)
            if feet:
                feet = feet.group(1)
                feet = int(feet) * 12
            else:
                feet = 0
            inches = re.search(r'\'(\d+)', height)
            if inches:
                inches = inches.group(1)
                inches = int(inches)
            else:
                inches = 0
            return str(int((feet + inches) * 2.54)) + "cm"
        return None

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'^(\d+)', weight)
        if weight:
            weight = weight.group(1)
            weight = str(int(int(weight) * .453592))
            return weight
        return None    