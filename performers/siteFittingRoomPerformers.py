import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
import re

def get_birthday_from_age(age):
    age = int(age.strip())
    if age >= 18 and age <= 99:
        birthdate = datetime.now() - relativedelta(years=age)
        birthdate = birthdate.strftime('%Y-%m-%d')
        return birthdate
    return ''
        

class FittingRoomPerformersSpider(BasePerformerScraper):
    name = 'FittingRoomPerformers'
    network = 'Fitting Room'
    parent = 'Fitting Room'
    site = 'Fitting Room'
    
    selector_map = {
        'name': '.model-profile-desc h2::text',
        'image': ".model-profile img::attr(src)",
        'bio': '.model-bio::text',
        'nationality': '//div[contains(@class, "model-profile-desc")]//p[1]/text()',
        'height': '//div[contains(@class, "model-profile-desc")]//p[3]/text()',
        'astrology': '//div[contains(@class, "model-profile-desc")]//p[4]/text()',
        'measurements': '//div[contains(@class, "model-profile-desc")]//p[5]/text()',
        'pagination': '/models/%s',
        'external_id': '\/models\/(.*)\/'
    }

    start_urls = [
        'https://www.fitting-room.com/',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumb item"]')
        for performer in performers:
            name = performer.xpath('./a/@title').get()
            image = performer.xpath('./a/div/img/@src').get()
            nationality = performer.xpath('./a/div/p[@class="item-text" and contains(text(),"Country:")]/span/text()').get()
            haircolor = performer.xpath('./a/div/p[@class="item-text" and contains(text(),"Hair:")]/span/text()').get()
            if haircolor == "Blond":
                haircolor = "Blonde"
            eyecolor = performer.xpath('./a/div/p[@class="item-text" and contains(text(),"Eyes:")]/span/text()').get()
            height = performer.xpath('./a/div/p[@class="item-text" and contains(text(),"Height:")]/span/text()').get()
            age = performer.xpath('./a/div/p[@class="item-text" and contains(text(),"Age:")]/span/text()').get()
            birthday = get_birthday_from_age(age)
            performer = performer.xpath('./a/@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer,
                meta={'name': name, 'image': image, 'birthday': birthday, 'nationality': nationality, 'haircolor': haircolor, 'eyecolor': eyecolor, 'height': height}
            )
            
     

