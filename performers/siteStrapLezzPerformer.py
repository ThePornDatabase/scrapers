import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteStrapLezzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//comment()[contains(.,"Model Thumbnail")]/following-sibling::img/@src0_3x',
        'height': '//dt[contains(text(),"Height")]/following-sibling::dd/text()',
        'bio': '//comment()[contains(.,"Bio Extra") and not(contains(.,"Fields"))]/following-sibling::p/text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': 'models\/(.*).html'
    }

    name = 'StrapLezzPerformer'
    network = "Strap Lezz"
    parent = "Strap Lezz"

    start_urls = [
        'https://straplezz.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model")]/a[contains(@href,"/models/")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_2x').get()
        if not image:
            image = response.xpath('//comment()[contains(.,"First Thumb")]/following-sibling::img/@src0_1x').get()
            
        if image:
            image = self.format_link(response, image)
            return image.replace(" ", "%20")

        return None
