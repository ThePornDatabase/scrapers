import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTouchMyWifePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="product-page"]/div/div/div/img/@src',
        'height': '//ul/li[contains(text(), "Height:")]/text()',
        'weight': '//ul/li[contains(text(), "Weight:")]/text()',
        'measurements': '//ul/li[contains(text(), "Meas:")]/text()',
        'eyecolor': '//ul/li[contains(text(), "Eyes:")]/text()',
        'haircolor': '//ul/li[contains(text(), "Hair:")]/text()',
        'ethnicity': '//ul/li[contains(text(), "Ethnicity:")]/text()',
        'pagination': '/porn-stars.html?sort=ag_added&page=%s&hybridview=member',
        'external_id': r'models\/(.*).html'
    }

    name = 'TouchMyWifePerformer'
    network = "Touch My Wife"

    start_urls = [
        'https://www.touchmywife.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item"]/a')
        for performer in performers:
            image = performer.xpath('./picture/source/@data-srcset')
            if image:
                image = image.get()
            else:
                image = False
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta={'image': image})

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
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements'))
            if cupsize:
                cupsize = cupsize.get()
                if "-" in cupsize:
                    cupsize = re.search(r'(\d+\w+)-\d+', cupsize)
                    if cupsize:
                        cupsize = cupsize.group(1).strip()
                if cupsize:
                    if " " in cupsize:
                        cupsize = cupsize.replace(" ", "")
                    return cupsize.strip()
        return ''

    def get_haircolor(self, response):
        haircolor = super().get_haircolor(response)
        if ":" in haircolor:
            haircolor = re.sub(r'^.*:', '', haircolor)
        return haircolor

    def get_eyecolor(self, response):
        eyecolor = super().get_eyecolor(response)
        if ":" in eyecolor:
            eyecolor = re.sub(r'^.*:', '', eyecolor)
        return eyecolor

    def get_ethnicity(self, response):
        ethnicity = super().get_ethnicity(response)
        if ":" in ethnicity:
            ethnicity = re.sub(r'^.*:', '', ethnicity)
        return ethnicity
