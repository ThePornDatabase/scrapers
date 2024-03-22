import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBaitBuddiesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-disc"]/h1/text()',
        'image': '//img[@class="profile-pic"]/@src',
        'image_blob': True,
        'eyecolor': '//div[@class="profile-body"]//text()[contains(.,"Eyes")]/following-sibling::b[1]/text()',
        'haircolor': '//div[@class="profile-body"]//text()[contains(.,"Hair")]/following-sibling::b[1]/text()',

        'pagination': '/?page=theguys&p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BaitBuddiesPerformer'
    network = 'Bait Buddies'

    start_urls = [
        'https://www.baitbuddies.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="theguys-thumb"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_weight(self, response):
        weight = response.xpath('//div[@class="profile-body"]//text()[contains(.,"Weight")]/following-sibling::b[1]')
        if weight:
            weight = weight.get()
            weight = re.search(r'(\d{2,3})', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .4535)) + "kg"
        return weight

    def get_height(self, response):
        height = response.xpath('//div[@class="profile-body"]//text()[contains(.,"Height")]/following-sibling::b[1]')
        if height:
            height = height.get()
            height = height.replace("``", "\"").replace("`", "'")
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
