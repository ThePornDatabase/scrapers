import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteClassLesbiansPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="banner-model"]/img/@src',
        'nationality': '//p[@class="country"]/text()',
        'pagination': '/models/%s',
        'external_id': 'models/(.+).html$'
    }

    name = 'ClassLesbiansPerformer'
    network = 'Class Media'

    start_urls = [
        'https://www.class-lesbians.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="box"]/a[contains(@href,"/models")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return "https://www.class-lesbians.com" + image.strip()
        return ''

