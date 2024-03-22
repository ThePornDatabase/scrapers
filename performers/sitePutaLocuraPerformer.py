import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem
from string import ascii_lowercase


class SitePutaLocuraPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/porn-actresses/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'SitePutaLocuraPerformer'

    start_urls = [
        'https://www.putalocura.com',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for char in ascii_lowercase:
            url = f"https://www.putalocura.com/en/porn-actresses/{char}"
            yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@class,"c-boxlist__box")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h2/text()').get())
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
            item['network'] = 'Puta Locura'
            item['url'] = self.format_link(response, performer.xpath('./@href').get())

            yield item
