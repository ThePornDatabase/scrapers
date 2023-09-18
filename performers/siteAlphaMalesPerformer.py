import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from scrapy.utils.project import get_project_settings
from tpdb.items import PerformerItem


class SitePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/modeles?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'AlphaMalesPerformer'
    network = 'Alpha Males'

    start_urls = [
        'https://www.alphamales.com',
    ]

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@href, "/en/modeles/detail")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div[2]/text()').get())
            item['image'] = performer.xpath('.//img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Male'
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
            item['network'] = 'Alpha Males'
            item['url'] = self.format_link(response, performer.xpath('./@href').get())

            yield item
