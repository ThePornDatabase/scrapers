import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SiteSwingingBiCouplesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': './a[1][contains(@href, "models")]/text()',
        'image': './a/img/@src0',

        'pagination': '/tour/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'SwingingBiCouplesPerformer'
    network = 'Swinging Bi Couples'

    start_urls = [
        'https://www.swingingbicouples.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.get_name(performer)
            image = performer.xpath('./a/img/@src0')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['image_blob'] = True
            item['bio'] = ''
            item['gender'] = ''
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Swinging Bi Couples'
            item['url'] = performer.xpath('./a[1]/@href').get()

            yield item
