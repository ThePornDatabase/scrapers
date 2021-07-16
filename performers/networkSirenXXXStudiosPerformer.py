import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class networkSirenXXXStudiosPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="modelBioArea"]//h2/text()',
        'image': '//div[@class="bioPic"]/img/@src0_1x',
        'cupsize': '//span[contains(text(),"Bust")]/following-sibling::text()',
        'height': '//span[contains(text(),"Height")]/following-sibling::text()',
        'bio': '//div[@class="about"]/p/text()',
        'pagination': '/modelbios.html',
        'external_id': 'models\/(.*).html'
    }

    name = 'SirenXXXStudiosPerformer'
    network = 'Siren XXX Studios'
    parent = 'Siren XXX Studios'

    start_urls = [
        'https://realnaughtynymphos.com',
        'https://myfirsttimesluts.com',
    ]

    def start_requests(self):
        for link in self.start_urls:
            url = link + "/tour/models/models.html"
            yield scrapy.Request(url,
                             callback=self.get_performers,
                             headers=self.headers,
                             cookies=self.cookies)                           
                                 
    def get_performers(self, response):
        performers = response.xpath('//div[@class="videoPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(performer, callback=self.parse_performer)

