import re
import json
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePassionPOVPerformerSpider(BasePerformerScraper):
    name = 'PassionPOVPerformer'

    selector_map = {
        'pagination': '',
        'external_id': r''
    }

    def start_requests(self):
        url = "https://passionpov.com/models?order_by=publish_date&gender="
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        jsoncode = response.xpath('//script[contains(text(), "pageProps")]/text()').get()
        if jsoncode:
            jsondata = json.loads(jsoncode)
            jsondata = jsondata['props']['pageProps']['models']['data']
            for row in jsondata:
                item = PerformerItem()
                item['name'] = string.capwords(row['name'])
                item['image'] = self.format_link(response, row['thumb'])
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['url'] = f"https://passionpov.com/models/{row['slug']}"
                item['network'] = 'PassionPOV'
                item['astrology'] = ''

                if 'bio' in row and row['Bio']:
                    item['bio'] = string.capwords(row['Bio'])
                else:
                    item['bio'] = ''

                item['birthday'] = ''
                if 'Birthdate' in row and row['Birthdate']:
                    if re.search(r'(\d{4}-\d{2}-\d{2})', str(row['Birthdate'])):
                        item['birthday'] = self.parse_date(row['Birthdate']).isoformat()

                if 'Born' in row and row['Born']:
                    item['birthplace'] = string.capwords(row['Born'])
                else:
                    item['birthplace'] = ''

                if 'Measurements' in row and row['Measurements']:
                    item['measurements'] = string.capwords(row['Measurements'])
                else:
                    item['measurements'] = ''

                item['cupsize'] = ''

                if 'Eyes' in row and row['Eyes']:
                    item['eyecolor'] = string.capwords(row['Eyes'])
                else:
                    item['eyecolor'] = ''

                if 'Hair' in row and row['Hair']:
                    item['haircolor'] = string.capwords(row['Hair'])
                else:
                    item['haircolor'] = ''

                item['height'] = ''
                item['weight'] = ''

                if 'sex' in row and row['gender']:
                    item['gender'] = string.capwords(row['gender'])
                else:
                    item['gender'] = 'Female'

                item['ethnicity'] = ''
                item['fakeboobs'] = ''
                item['nationality'] = ''
                item['piercings'] = ''
                item['tattoos'] = ''
                yield item
