import json
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMrBigfatdickPerformerSpider(BasePerformerScraper):
    name = 'MrBigfatdickPerformer'
    network = 'MrBigfatdick'

    url = "https://backend.mrbigfatdick.com/api/public/models"

    selector_map = {
        'external_id': r'movie/(.+)',
        'pagination': 'https://backend.mrbigfatdick.com/api/public/models'
    }

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        global json
        performers = json.loads(response.text)

        for performer in performers:
            item = PerformerItem()

            item['name'] = string.capwords(performer['fullName'])
            item['image'] = performer['previewImage960']
            if not item['image']:
                item['image'] = None
            item['image_blob'] = None
            item['url'] = "https://www.mrbigfatdick.com/models/" + performer['permaLink']
            item['height'] = str(performer['height']) + "cm"
            item['weight'] = str(performer['weight']) + "kg"

            if performer['eyes']:
                item['eyecolor'] = performer['eyes'].title()
            else:
                item['eyecolor'] = ''

            if performer['hair']:
                item['haircolor'] = performer['hair'].title()
            else:
                item['haircolor'] = ''

            if "m" in performer['gender']:
                item['gender'] = "Male"
            else:
                item['gender'] = "Female"

            item['network'] = 'MrBigfatdick'

            if performer['description']:
                item['bio'] = performer['description'].title()
            else:
                item['bio'] = ''

            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['fakeboobs'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''

            yield item
