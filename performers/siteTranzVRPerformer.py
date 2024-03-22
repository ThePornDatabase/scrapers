import json
import scrapy
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteTranzVRPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?o=d&p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'TranzVRPerformer'
    network = 'TranzVR'

    start_urls = [
        'https://www.tranzvr.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//li[contains(@class,"cards-list__item")]/div[1]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def parse_performer(self, response):
        performer = response.xpath('//script[contains(@type, "ld+json")]/text()').get()
        performer = json.loads(performer)
        item = PerformerItem()

        item['name'] = performer['name']

        image = performer['image']
        if image:
            item['image'] = self.format_link(response, image)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ""
            item['image_blob'] = ""

        item['bio'] = ''
        if "trans" in performer['gender'].lower():
            item['gender'] = 'Trans Female'
        else:
            item['gender'] = 'Female'

        if "birthDate" in performer and performer['birthDate']:
            item['birthday'] = performer['birthDate']
        else:
            item['birthday'] = ''

        if "birthPlace" in performer and performer['birthPlace']:
            item['birthplace'] = performer['birthPlace']
        else:
            item['birthplace'] = ''

        item['astrology'] = ''
        item['cupsize'] = ''
        item['ethnicity'] = ''
        item['eyecolor'] = ''
        item['fakeboobs'] = ''
        item['haircolor'] = ''

        if "height" in performer and performer['height']:
            item['height'] = performer['height'].replace(" ", "")
        else:
            item['height'] = ''

        item['measurements'] = ''
        item['nationality'] = ''
        item['piercings'] = ''
        item['tattoos'] = ''
        item['weight'] = ''
        item['network'] = 'TranzVR'
        item['url'] = response.url

        yield item
