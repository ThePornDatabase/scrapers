import scrapy
import re
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteYanksPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="item-thumb"]/img/@src0_1x|//div[@class="item-thumb"]/img/@src0',
        'height': '//span[contains(text(),"Height")]/following-sibling::text()[1]',
        'astrology': '//span[contains(text(),"Astrological")]/following-sibling::text()[1]',
        'haircolor': '//span[contains(text(),"Hair Color")]/following-sibling::text()[1]',
        'eyecolor': '//span[contains(text(),"Eye Color")]/following-sibling::text()[1]',
        'birthplace': '//span[contains(text(),"Hometown")]/following-sibling::text()[1]',
        'bio': '//div[contains(@class, "model-bio")]/p//text()',
        'pagination': '/models/models_%s.html',
        'external_id': r'models\/(.*).html'
    }

    name = 'YanksPerformer'
    network = 'Yanks'

    start_urls = [
        'https://www.yanks.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item-update")]/div[1]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_height(self, response):
        height = super().get_height(response)
        if "'" in height:
            height = re.sub(r'[^0-9\'\"]+', '', height)
            height = re.search(r'(\d+)\'(\d+)', height)
            if height:
                feet = int(height.group(1)) * 12
                inches = int(height.group(2))
                height = str(int((feet + inches) * 2.54)) + "cm"
                return height
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            return ""
        return image
