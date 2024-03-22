import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SitePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': "",
        'external_id': r'model/(.*)/'
    }

    name = 'PervectPerformer'
    network = 'Pervect'

    start_urls = [
        'https://pervect.com/models/',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        url = "https://pervect.com/models/"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@class, "model-item")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[contains(@class, "model-name")]/text()').get()).replace("-", "")
            item['image'] = performer.xpath('.//img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ""
            item['gender'] = "Female"
            item['astrology'] = ""
            item['birthday'] = ""
            item['birthplace'] = ""
            item['cupsize'] = ""
            item['ethnicity'] = ""
            item['eyecolor'] = ""
            item['fakeboobs'] = ""
            item['haircolor'] = ""
            item['height'] = ""
            item['measurements'] = ""
            item['nationality'] = ""
            item['piercings'] = ""
            item['tattoos'] = ""
            item['weight'] = ""
            item['network'] = "Pervect"
            item['url'] = performer.xpath('./@href').get()

            yield item
