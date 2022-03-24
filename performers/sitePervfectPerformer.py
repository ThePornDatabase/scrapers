import json
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePervfectPerformerSpider(BasePerformerScraper):
    name = 'PervfectPerformer'

    selector_map = {
        'pagination': '',
        'external_id': r''
    }

    def start_requests(self):
        url = "http://www.pervfect.net/api/v1/performers?limit=500&offset=0&status=active&sort=sort&order=1&keyword=&sex=&size="
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        jsondata = json.loads(response.text)
        for row in jsondata:
            item = PerformerItem()
            item['name'] = string.capwords(row['name'])
            item['image'] = self.format_link(response, row['imageMediumPath'])
            item['image_blob'] = None
            item['url'] = f"http://www.pervfect.net/models/{row['alias']}/{row['_id']}"
            item['network'] = 'Pervfect'
            item['astrology'] = ''
            if 'sexualPreferences' in row and row['sexualPreferences']:
                item['bio'] = string.capwords(row['sexualPreference'])
            else:
                item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''

            if 'ethnicity' in row and row['ethnicity']:
                item['ethnicity'] = string.capwords(row['ethnicity'])
            else:
                item['ethnicity'] = ''

            if 'eyes' in row and row['eyes']:
                item['eyecolor'] = string.capwords(row['eyes'])
            else:
                item['eyecolor'] = ''

            if 'hair' in row and row['hair']:
                item['haircolor'] = string.capwords(row['hair'])
            else:
                item['haircolor'] = ''

            if 'sex' in row and row['sex']:
                item['gender'] = string.capwords(row['sex'])
            else:
                item['gender'] = 'Female'

            item['fakeboobs'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            yield item
