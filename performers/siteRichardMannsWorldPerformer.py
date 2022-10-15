import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteRichardMannsWorldPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[@itemprop="name"]/text()',
        'image': '//div[@class="psImg"]/img/@src',
        'bio': '//span[@itemprop="description"]//text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '//strong[contains(text(), "Bra Size")]/following-sibling::text()',
        'ethnicity': '',
        'eyecolor': '//strong[contains(text(), "Eye Color")]/following-sibling::text()',
        'fakeboobs': '',
        'haircolor': '//strong[contains(text(), "Hair Color")]/following-sibling::text()',
        'height': '//span[@itemprop="Height"]/text()',
        'measurements': '//strong[contains(text(), "Measurement")]/following-sibling::text()',
        'nationality': '//span[@itemprop="nationality"]/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '//span[@itemprop="Weight"]/text()',

        'pagination': '/pornstars/page/%s/?sort=latest',
        'external_id': r'model/(.*)/'
    }

    name = 'RichardMannsWorldPerformer'
    network = 'Richard Manns World'

    start_urls = [
        'https://richardmannsworld.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="latestPS"]/ul/li/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'(\d{2,3})', weight)
        if weight:
            weight = weight.group(1)
            weight = str(round(int(weight) * .45359237)) + "kg"
            return weight
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        height = re.search(r'(\d).*?(\d{1,2})', height)
        if height:
            feet = int(height.group(1))
            inches = int(height.group(2))
            cm = round((inches + (feet * 12)) * 2.54)
            return str(cm) + "cm"
        return ''

    def get_measurements(self, response):
        measurements = super().get_measurements(response)
        measurements = measurements.replace(" ", "-")
        return measurements
