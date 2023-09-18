import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SiteSensexPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'SensexPerformer'
    network = 'Sensex'

    start_urls = [
        'https://www.sensex.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href, "/profile/")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="overlay"]/p[1]/text()').get())
            item['image'] = performer.xpath('.//div/img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*)\?', performer.xpath('.//div/img/@src').get()).group(1)
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
            item['network'] = 'Sensex'
            item['url'] = self.format_link(response, performer.xpath('./@href').get())

            yield item
