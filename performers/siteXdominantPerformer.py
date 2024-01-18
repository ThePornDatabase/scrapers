import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteXdominantPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'XdominantPerformer'

    start_urls = [
        'https://xdominant.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[@class="models__item"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//span[@class="models__name"]/text()').get()
            item['name'] = self.cleanup_title(string.capwords(name.strip(" X")))
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            item['gender'] = 'Female'
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
            item['network'] = 'XDominant Official'
            item['url'] = self.format_link(response, performer.xpath('./@href').get())

            yield item

