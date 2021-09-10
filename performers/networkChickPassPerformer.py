import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkChickPassPerformerSpider(BasePerformerScraper):

    selector_map = {
        'name': '//span[@class="title_bar_hilite"]/text()',
        'image': '//div[@class="row model_bio_wrapper"]/div/img/@src0_3x',
        'birthplace': '//p[@class="model__stat"]/span[contains(text(), "Location")]/following-sibling::text()',
        'height': '//p[@class="model__stat"]/span[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//p[@class="model__stat"]/span[contains(text(), "Weight")]/following-sibling::text()',
        'astrology': '//p[@class="model__stat"]/span[contains(text(), "Astrological Sign")]/following-sibling::text()',
        'measurements': '//p[@class="model__stat"]/span[contains(text(), "Measurements")]/following-sibling::text()',
        'bio': '//div[@class="model_bio_info"]/text()',
        'pagination': '/tour1/categories/models_%s.html',
        'external_id': r'.*\/(.*)\/$'
    }

    name = 'ChickPassPerformer'
    network = 'Chick Pass'

    start_urls = [
        'https://www.chickpass.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                str_height = re.findall(r'(\d{1,2})', height)
                if len(str_height):
                    feet = int(str_height[0])
                    if len(str_height) > 1:
                        inches = int(str_height[1])
                    else:
                        inches = 0
                    heightcm = str(round(((feet * 12) + inches) * 2.54)) + "cm"
                    return heightcm.strip()
        return ''

    def get_weight(self, response):
        weight = super().get_weight(response)
        return weight.replace(" ", "")

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                if "-" in measurements:
                    cupsize = re.search('(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.strip()
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        return self.format_link(response, image)
