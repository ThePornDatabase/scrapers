import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteCospuriPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="name-en"]/text()',
        'image': '//div[@class="model-costume"]/@style',
        'bio': '//div[contains(@class,"hidden-xs")]/p/text()',
        'nationality': '//div[@class="item country"]/span/text()',
        'height': '//div[@class="item height"]/span/text()',
        'country': '//div[@class="item country"]/span/text()',
        'measurements': '//div[@class="item measurements"]/span/text()',
        'pagination': '/models/page/%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'CospuriPerformer'
    network = 'Cospuri'

    start_urls = [
        'https://www.cospuri.com',
    ]

    def start_requests(self):
        url = "https://www.cospuri.com/models/"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model-thumb")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'B\d{2,3}.*?W\d{2,3}.*?H\d{2,3}', measurements):
                bust = re.search(r'B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust) / 2.54)
                waist = re.search(r'W(\d{2,3})', measurements).group(1)
                if waist:
                    waist = round(int(waist) / 2.54)
                hips = re.search(r'H(\d{2,3})', measurements).group(1)
                if hips:
                    hips = round(int(hips) / 2.54)

                cupsize = re.search(r'B\d+-([a-zA-Z]+)', measurements)
                if cupsize:
                    cupsize = cupsize.group(1)
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        cupsize = cupsize.strip()

                if bust and waist and hips and cupsize:
                    measurements = str(bust) + cupsize + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
                if bust and waist and hips:
                    measurements = str(bust) + "-" + str(waist) + "-" + str(hips)
                    return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'B\d{2,3}.*?W\d{2,3}.*?H\d{2,3}', measurements):
                bust = re.search(r'B(\d{2,3})', measurements).group(1)
                if bust:
                    bust = round(int(bust) / 2.54)

                cupsize = re.search(r'B\d+-([a-zA-Z]+)', measurements)
                if cupsize:
                    cupsize = cupsize.group(1)
                    if cupsize == "N/A":
                        cupsize = ''
                    else:
                        cupsize = cupsize.strip()

                if bust and cupsize:
                    cupsize = str(bust) + cupsize
                    return cupsize.strip()
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search(r'(http.*\.jpg)', image).group(1)
            if image:
                return self.format_link(response, image.strip())
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cm" in height and re.match(r'(\d+\s?cm)', height):
                    height = re.search(r'(\d+\s?cm)', height).group(1).strip()
                    height = height.replace(" ", "")
                if "0 ft" not in height:
                    return height.strip()
        return ''
