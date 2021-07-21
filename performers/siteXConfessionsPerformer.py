import scrapy
import re

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem

class siteXConfessionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[contains(text(),"About")]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/performers?page=%s',
        'external_id': 'models\/(.*).html'
    }

    name = 'XConfessionsPerformer'
    network = "XConfessions"
    parent = "XConfessions"

    start_urls = [
        'https://xconfessions.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"overflow-hidden") and ./a[contains(@href,"/performers/")]]')
        for performer in performers:
            item = PerformerItem()
            
            name = performer.xpath('.//a/p/text()').get()
            if name:
                item['name'] = name.strip()
            else:
                item['name'] = ''
                
            image = performer.xpath('.//source/@data-srcset').get()
            if image:
                image = re.search('(.*)\?', image).group(1)
                if image:
                    item['image'] = image.strip()
                
            if not image:
                item['image'] = ''
                
            url = performer.xpath('./div/a/@href').get()
            if url:
                item['url'] = "https://xconfessions.com/" + url.strip()
            else:
                item['url'] = ''
                
            item['network'] = 'XConfessions'
            
            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
