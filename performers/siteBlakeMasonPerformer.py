import re
import json
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBlakeMasonPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': 'https://blakemason.com/models?page=%s&order_by=publish_date&sort_by=desc',
        'external_id': r'model/(.*)/'
    }

    name = 'BlakeMasonPerformer'
    network = 'Blake Mason'

    start_urls = [
        'https://blakemason.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        jsondata = json.loads(response.xpath('//script[contains(@id, "__NEXT_DATA__")]/text()').get())
        jsondata = jsondata['props']['pageProps']['models']['data']
        for performer in jsondata:
            item = PerformerItem()

            item['name'] = performer['name']
            item['image'] = performer['thumbnail']
            if "http" not in item['image']:
                item['image'] = "https:" + item['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = performer['Bio']
            if "gender" in performer and performer['gender']:
                item['gender'] = string.capwords(performer['gender'])
            else:
                item['gender'] = "Male"
            item['astrology'] = ''
            if "Birthdate" in performer and performer['Birthdate']:
                item['birthday'] = performer['Birthdate']
            else:
                item['birthday'] = ''

            if "Born" in performer and performer['Born']:
                item['birthplace'] = performer['Born']
            else:
                item['birthplace'] = ''

            item['measurements'] = ''
            item['cupsize'] = ''

            if "race" in performer and performer['race']:
                item['ethnicity'] = performer['race'].title()
            else:
                item['ethnicity'] = ""

            if "eyes" in performer and performer['eyes']:
                item['eyecolor'] = performer['eyes']
            else:
                item['eyecolor'] = ''
            item['fakeboobs'] = ''

            if "hair" in performer and performer['hair']:
                item['haircolor'] = performer['hair']
            else:
                item['haircolor'] = ''

            if "height" in performer and performer['height']:
                item['height'] = self.get_height(performer['height'])
            else:
                item['height'] = ''

            if "weight" in performer and performer['weight']:
                item['weight'] = self.get_height(performer['weight'])
            else:
                item['weight'] = ''

            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['network'] = 'Blake Mason'
            item['url'] = f"https://blakemason.com/models/{performer['slug']}"

            yield item

    def get_weight(self, weight):
        if weight:
            weight = int(weight)
            weight = int(weight * .45)
        return str(weight) + "kg"

    def get_height(self, height):
        if "'" in height:
            height = re.sub(r'[^0-9\']', '', height)
            feet = re.search(r'(\d+)\'', height)
            if feet:
                feet = feet.group(1)
                feet = int(feet) * 12
            else:
                feet = 0
            inches = re.search(r'\'(\d+)', height)
            if inches:
                inches = inches.group(1)
                inches = int(inches)
            else:
                inches = 0
            return str(int((feet + inches) * 2.54)) + "cm"
        return None
