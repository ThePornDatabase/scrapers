import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSuperbeModelsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"section-boxed")]//h1/text()',
        'image': '//img[contains(@class, "poster-thumb")]/@src',
        'nationality': '//span[@class="girl-info-label" and contains(text(), "Nationality")]/following-sibling::span/text()',
        'haircolor': '//span[@class="girl-info-label" and contains(text(), "Hair")]/following-sibling::span/text()',
        'eyecolor': '//span[@class="girl-info-label" and contains(text(), "Eyes")]/following-sibling::span/text()',
        'height': '//span[@class="girl-info-label" and contains(text(), "Height")]/following-sibling::span/text()',
        'bio': '//div[@class="girl-description"]//text()',
        'pagination': '/pornstars/sex/girls.en.html?order=activity&page=%s',
        'external_id': r'models\/(.*).html'
    }

    name = 'SuperbeModelsPerformer'
    network = "Superbe Models"

    start_urls = [
        'https://superbe.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "global-multi-card")]/div/a/@href ').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_image(self, response):
        image = re.search(r'girl-image lazy.*?data-bg=\"(.*?)\"', response.text)
        if image:
            return image.group(1)
        return ""
