import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSocialGlamourPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="product-page"]/div/div/div/img/@src',
        'height': '//div[@class="modelinfo"]/div[contains(text(), "height")]/following-sibling::div[1]/text()',
        'weight': '//div[@class="modelinfo"]/div[contains(text(), "weight")]/following-sibling::div[1]/text()',
        'measurements': '//div[@class="modelinfo"]/div[contains(text(), "measurements")]/following-sibling::div[1]/text()',
        'cupsize': '//div[@class="modelinfo"]/div[contains(text(), "breasts")]/following-sibling::div[1]/text()',
        'eyecolor': '//div[@class="modelinfo"]/div[contains(text(), "eyecolor")]/following-sibling::div[1]/text()',
        'haircolor': '//div[@class="modelinfo"]/div[contains(text(), "haircolor")]/following-sibling::div[1]/text()',
        'astrology': '//div[@class="modelinfo"]/div[contains(text(), "sign")]/following-sibling::div[1]/text()',
        'nationality': '//div[@class="modelinfo"]/div[contains(text(), "country")]/following-sibling::div[1]/text()',
        'bio': '//div[@class="description"]/text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': r'models\/(.*).html'
    }

    name = 'SocialGlamourPerformer'
    network = "Social Glamour"

    start_urls = [
        'https://www.socialglamour.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="product-item"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

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
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                if re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                    measurements = re.sub(r'[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        cupsize = super().get_cupsize(response)
        if "-" in cupsize:
            cupsize = re.search(r'(\d{2,3}\w{1,3})', cupsize)
            if cupsize:
                cupsize = cupsize.group(1).strip()
        return cupsize.replace(" ", "").strip()
