import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteHouseOfGordPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    cookies = {'legal_accepted2': 'yes'}

    name = 'HouseOfGordPerformer'
    network = 'House Of Gord'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        url = "https://www.houseofgord.com/models"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//table[contains(@class, "participant_listing")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//a[contains(@class, "participant")]/text()').get())
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(image)
            else:
                item['image'] = ''
                item['image_blob'] = ''
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
            item['network'] = 'House Of Gord'
            item['url'] = self.format_link(response, performer.xpath('.//a[contains(@class, "participant")]/@href').get())

            yield item
