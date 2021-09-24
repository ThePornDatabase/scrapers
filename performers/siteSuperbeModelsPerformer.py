import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSuperbeModelsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "modelContainerHeading")]/h2/text()',
        'image': '//div[@class="img"]/a/img/@src',
        'birthplace': '//ul[@class="model-list"]/li[contains(text(), "City")]/span/text()',
        'nationality': '//ul[@class="model-list"]/li[contains(text(), "Country")]/span/text()',
        'height': '//ul[@class="model-list"]/li[contains(text(), "Height")]/span/text()',
        'weight': '//ul[@class="model-list"]/li[contains(text(), "Weight")]/span/text()',
        'bio': '//div[contains(@class,"text-desc-2")]/text()',
        'pagination': '/models/page-%s/?tag=&sort=recent&pussy=all&',
        'external_id': r'models\/(.*).html'
    }

    name = 'SuperbeModelsPerformer'
    network = "Superbe Models"

    start_urls = [
        'https://www.superbemodels.com/model/all/'
    ]

    def start_requests(self):
        url = "https://www.superbemodels.com/model/all/"
        yield scrapy.Request(url, callback=self.get_performers, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@id="list_models_models_list_items"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

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
        height = re.search(r'(\d).(\d{1,2})', height)
        if height:
            feet = int(height.group(1))
            inches = int(height.group(2))
            cm = round((inches + (feet * 12)) * 2.54)
            return str(cm) + "cm"
        return ''
