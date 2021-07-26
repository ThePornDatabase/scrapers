import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteColetteSpider(BasePerformerScraper):
    name = 'ColettePerformer'
    network = "BC Media"

    start_urls = [
        'https://www.colette.com',
    ]

    cookies = {
        '_warning': 'true',
    }
    
    selector_map = {
        'name': '//div[contains(@class,"info-wrapper")]//h1/text()',
        'image': '//div[contains(@class,"info-wrapper")]//img/@data-interchange',
        'nationality': '//div[contains(@class,"info-wrapper")]//span[contains(text(),"Country:")]/following-sibling::text()',
        'bio': '//div[contains(@class,"info-wrapper")]//p/text()',
        'pagination': '/index.php?show=models&sort=recent&page=%s',
        'external_id': 'models\/(.*).html'
    }
                                 
    def get_performers(self, response):
        performers = response.xpath('//ul[contains(@class,"small-block-grid-1")]/li/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(performer, callback=self.parse_performer)


    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                image = re.search('.*\[(http.*lrg.jpg)', image).group(1).replace(" ","%20")
                if image:
                    return image.strip()
        return ''

    def get_gender(self, response):
        return "Female"
