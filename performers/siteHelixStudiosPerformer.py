import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[contains(@class,"model-headshot-image-wrapper")]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="description"]/p/text()',
        'eyecolor': '//span[contains(text(), "Eyes")]/following-sibling::text()',
        'haircolor': '//span[contains(text(), "Hair") and not(contains(text(), "Body"))]/following-sibling::text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//span[contains(text(), "Weight")]/following-sibling::text()',

        'pagination': '/models/page/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'HelixStudiosPerformer'
    network = 'Helix Studios'

    start_urls = [
        'https://www.helixstudios.com',
    ]

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"grid-item")]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_weight(self, response):
        weight = response.xpath('//span[contains(text(), "Weight")]/following-sibling::text()')
        if weight:
            weight = weight.get()
            weight = re.search(r'(\d+)', weight)
            if weight:
                return str(int(int(weight.group(1)) * .453592)) + "kg"
        return None

    def get_height(self, response):
        height = response.xpath('//span[contains(text(), "Height")]/following-sibling::text()')
        if height:
            height = height.get()
            height = height.replace('&#039;', "'")
            height = re.sub(r'[^0-9\']+', '', height)
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'\d+?\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None
