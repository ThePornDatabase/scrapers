import re
import json
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteInsertedPerformerSpider(BasePerformerScraper):
    name = 'InsertedPerformer'

    selector_map = {
        'pagination': '',
        'external_id': r''
    }

    def start_requests(self):
        url = "https://inserted.com/tour/models"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        jsoncode = response.xpath('//script[contains(text(), "window.__DATA__")]/text()')
        if jsoncode:
            jsoncode = re.search(r'({.*})\s+window', jsoncode.get()).group(1)
            jsondata = json.loads(jsoncode)
            jsondata = jsondata['models']['items']
            for row in jsondata:
                item = PerformerItem()
                item['name'] = string.capwords(row['name'])
                item['image'] = self.format_link(response, row['thumb'])
                item['image_blob'] = None
                short_name = row['name'].lower().replace(" ", "-")
                item['url'] = f"https://inserted.com/tour/models/{row['id']}/{short_name}"
                item['network'] = 'Inserted'
                item['astrology'] = ''

                if 'bio' in row['attributes'] and row['attributes']['bio']['value']:
                    item['bio'] = string.capwords(row['attributes']['bio']['value'])
                else:
                    item['bio'] = ''

                item['birthday'] = ''
                if 'birthdate' in row['attributes'] and row['attributes']['birthdate']['value']:
                    if re.search(r'(\d{4}-\d{2}-\d{2})', str(row['attributes']['birthdate']['value'])):
                        item['birthday'] = self.parse_date(row['attributes']['birthdate']['value']).isoformat()

                if 'birthplace' in row['attributes'] and row['attributes']['birthplace']['value']:
                    item['birthplace'] = string.capwords(row['attributes']['birthplace']['value'])
                else:
                    item['birthplace'] = ''

                item['measurements'] = ''
                item['cupsize'] = ''
                if 'measurements' in row['attributes'] and row['attributes']['measurements']['value']:
                    if re.search(r'(\d{1,3}\w{1,5}-\d{1,3}-\d{1,3})', row['attributes']['measurements']['value']):
                        item['measurements'] = row['attributes']['measurements']['value']
                        item['cupsize'] = re.search(r'(\d{1,3}\w{1,5})-\d{1,3}-\d{1,3}', row['attributes']['measurements']['value']).group(1)

                if 'eyes' in row['attributes'] and row['attributes']['eyes']['value']:
                    item['eyecolor'] = string.capwords(row['attributes']['eyes']['value'])
                else:
                    item['eyecolor'] = ''

                if 'hair' in row['attributes'] and row['attributes']['hair']['value']:
                    item['haircolor'] = string.capwords(row['attributes']['hair']['value'])
                else:
                    item['haircolor'] = ''

                if 'height' in row['attributes'] and row['attributes']['height']['value']:
                    item['height'] = string.capwords(row['attributes']['height']['value'])
                else:
                    item['height'] = ''

                if 'weight' in row['attributes'] and row['attributes']['weight']['value']:
                    item['weight'] = string.capwords(row['attributes']['weight']['value'])
                else:
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
