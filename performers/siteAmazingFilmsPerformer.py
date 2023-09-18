import re
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteAmazingFilmsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/_next/data/u0ZVczEZX0D_vbAprl4x_/models.json?order_by=views&sort_by=desc&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'AmazingFilmsPerformer'
    network = 'Amazing Films'

    start_urls = [
        'https://amazingfilms.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['models']['data']
        for performer in jsondata:
            item = PerformerItem()

            item['name'] = performer['name']
            item['image'] = performer['thumb']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            if "gender" in performer and performer['gender']:
                item['gender'] = string.capwords(performer['gender'])
            else:
                item['gender'] = "female"
            item['astrology'] = ''
            if "Birthdate" in performer and performer['Birthdate']:
                item['birthday'] = performer['Birthdate']
            else:
                item['birthday'] = ''

            if "Born" in performer and performer['Born']:
                item['birthplace'] = performer['Born']
            else:
                item['birthplace'] = ''

            if "Measurements" in performer and performer['Measurements']:
                item['measurements'] = performer['Measurements']
            else:
                item['measurements'] = ''

            if re.search(r'(\d+\w+)-', item['measurements']):
                item['cupsize'] = re.search(r'(\d+\w+)-', item['measurements']).group(1)
            else:
                item['cupsize'] = ''

            item['ethnicity'] = ''

            if "Eyes" in performer and performer['Eyes']:
                item['eyecolor'] = performer['Eyes']
            else:
                item['eyecolor'] = ''
            item['fakeboobs'] = ''

            if "Hair" in performer and performer['Hair']:
                item['haircolor'] = performer['Hair']
            else:
                item['haircolor'] = ''

            if "Height" in performer and performer['Height']:
                item['height'] = self.get_height(performer['Height'])
            else:
                item['height'] = ''

            if "Weight" in performer and performer['Weight']:
                item['weight'] = self.get_height(performer['Weight'])
            else:
                item['weight'] = ''

            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['network'] = 'Amazing Films'
            item['url'] = f"https://amazingfilms.com/models/{performer['slug']}"

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
