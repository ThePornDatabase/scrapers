import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBreedItRawPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'weight': '//strong[contains(text(),"Weight")]/following-sibling::text()',
        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': 'models\/(.*).html'
    }

    name = 'BreedItRawPerformer'
    network = 'Breed It Raw'

    start_urls = [
        'https://breeditraw.net',
    ]

    def get_gender(self, response):
        return 'Male'


    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = name.replace("About", "").strip()
        return name
        
    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site':'Breed It Raw'}
            )

    def get_bio(self, response):
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if " " in image:
                    image = re.search('(.*) ', image).group(1)
                if image:
                    image = image.replace('//','/')
                    image = 'http://breeditraw.net' + image
                    return image.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
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

    def get_weight(self, response):
        weight = super().get_weight(response)
        weight = re.search(r'^(\d+)', weight)
        if weight:
            weight = weight.group(1)
            weight = str(int(int(weight) * .453592))
            return weight
        return None    