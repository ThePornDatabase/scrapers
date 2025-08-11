import scrapy
import re
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteCumHereBoyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[@class="title"]/a/following-sibling::text()',
        're_name': r'/ (.*)',
        'image': '//div[@class = "updatesBlock"]//img/@src0_2x',
        'bio': '//comment()[contains(.,"Bio Extra") and not(contains(., "Fields"))]/following-sibling::text()',
        'pagination': '/models/models_%s.html',
        'external_id': r'models\/(.*).html'
    }

    name = 'CumHereBoyPerformer'
    network = 'CumHereBoy'

    start_urls = [
        'https://cumhereboy.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_gender(self, response):
        return "Male"

    def get_weight(self, response):
        weight = response.xpath('//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Weight")]')
        if weight:
            weight = weight.get()
            weight = re.sub(r'[^0-9a-z]+', '', weight.lower())
            weight = re.search(r'(\d{2,3})', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .4535)) + "kg"
        return weight

    def get_height(self, response):
        height = response.xpath('//span[@class="model_bio_heading"]/following-sibling::text()[contains(., "Height")]')
        if height:
            height = height.get()
            height = height.replace("``", "\"").replace("`", "'")
            height = re.sub(r'[^0-9a-z\'\"]+', '', height.lower())
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
