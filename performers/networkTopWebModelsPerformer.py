import re
import json

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class TopWebModelsSpider(BasePerformerScraper):
    name = 'TopWebModelsPerformer'
    network = 'TopWebModels'

    start_urls = [
        'https://tour.topwebmodels.com/'
    ]

    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': ''
    }

    def get_performers(self, response):
        global json
        responseresult = response.xpath('//script[contains(text(),"window.__DATA__")]/text()').get()
        responsedata = re.search(r'__DATA__\ =\ (.*)', responseresult).group(1)
        jsondata = json.loads(responsedata)
        data = jsondata['data']['models']['items']
        for jsonentry in data:
            item = PerformerItem()
            item['gender'] = "Female"
            item['name'] = jsonentry['name']
            item['image'] = jsonentry['thumb']
            urltext = re.sub(r'[^A-Za-z0-9 ]+', '', jsonentry['name']).lower()
            urltext = urltext.replace("  ", " ")
            urltext = urltext.replace(" ", "-")
            urltext = "https://tour.topwebmodels.com/models/" + str(jsonentry['id']) + "/" + urltext
            item['url'] = urltext
            item['network'] = 'TopWebModels'

            if 'birthdate' in jsonentry['attributes']:
                item['birthday'] = jsonentry['attributes']['birthdate']['value']
            else:
                item['birthday'] = ''

            if 'born' in jsonentry['attributes']:
                item['birthplace'] = jsonentry['attributes']['born']['value']
            else:
                item['birthplace'] = ''

            if 'ethnicity' in jsonentry['attributes']:
                item['ethnicity'] = jsonentry['attributes']['ethnicity']['value']
            else:
                item['ethnicity'] = ''

            if 'hair' in jsonentry['attributes']:
                item['haircolor'] = jsonentry['attributes']['hair']['value']
            else:
                item['haircolor'] = ''

            if 'eyes' in jsonentry['attributes']:
                item['eyecolor'] = jsonentry['attributes']['eyes']['value']
            else:
                item['eyecolor'] = ''

            if 'weight' in jsonentry['attributes']:
                item['weight'] = jsonentry['attributes']['weight']['value']
            else:
                item['weight'] = ''

            if item['weight']:
                item['weight'] = str(item['weight']) + "lbs"

            if 'height' in jsonentry['attributes']:
                item['height'] = jsonentry['attributes']['height']['value']
            else:
                item['height'] = ''

            if 'measurements' in jsonentry['attributes']:
                item['measurements'] = jsonentry['attributes']['measurements']['value']
            else:
                item['measurements'] = ''

            if item['measurements'] and re.match('(.*-.*-.*)', item['measurements']):
                cupsize = re.search(r'(?:\s+)?(.*)-.*-', item['measurements']).group(1)
                if cupsize:
                    item['cupsize'] = cupsize
                else:
                    item['cupsize'] = ''
            else:
                item['cupsize'] = ''

            # Couldn't find examples on site
            item['bio'] = ''
            item['astrology'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['fakeboobs'] = ''
            item['tattoos'] = ''
            item['image_blob'] = None

            if self.debug:
                print(item)
            else:
                yield item

            item.clear()
