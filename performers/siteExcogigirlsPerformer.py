import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteExcogigirlsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[contains(@class, "model-name")]/text()',
        'image': '//img[contains(@class, "model_bio_thumb")]/@src0_1x',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'ExcogigirlsPerformer'
    network = 'Excogigirls'

    start_urls = [
        'https://excogigirls.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="content-div"]/h4/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements):
                measurements = re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements)
                measurements = measurements.group(1) + "-" + measurements.group(2) + "-" + measurements.group(3)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements):
                cupsize = re.search(r'(\d+\w+).*?(\d+).*?(\d+)', measurements).group(1)
                if cupsize:
                    return cupsize.strip()
            return cupsize.strip()
        return ''
