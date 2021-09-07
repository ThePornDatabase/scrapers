import re
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSubspacelandPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model-details"]/h1/text()',
        'image': '//div[@class="model-photo"]/img/@src',
        'nationality': '//span[contains(text(), "Country")]/following-sibling::text()',
        'height': '//span[contains(text(), "Height")]/following-sibling::text()',
        'fakeboobs': '//span[contains(text(), "Boobs")]/following-sibling::text()',
        'pagination': '/models/%s',
        'external_id': '/models/5'
    }

    name = 'SubspacelandPerformer'
    network = "Subspaceland"

    start_urls = [
        'https://www.subspaceland.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="ModelsAsItem"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_fakeboobs(self, response):
        if 'fakeboobs' in self.selector_map:
            fakeboobs = self.process_xpath(response, self.get_selector_map('fakeboobs')).get()
            if fakeboobs:
                if "enhanced" in fakeboobs.lower():
                    return "Yes"
                if "natural" in fakeboobs.lower():
                    return "No"
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        image = self.format_link(response, image)
        return image

    def get_height(self, response):
        height = super().get_height(response).lower()
        height = re.search(r'(\d{3} ?cm)', height)
        if height:
            height = height.group(1)
            height = height.replace(" ", "")
        return height

    def get_name(self, response):
        return string.capwords(self.process_xpath(response, self.get_selector_map('name')).get().strip())
