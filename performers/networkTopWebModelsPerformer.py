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
        responseresult = response.xpath('//script[contains(@id,"NEXT_DATA")]/text()').get()
        jsondata = json.loads(responseresult)
        data = jsondata['props']['pageProps']['models']['data']
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

            if 'Birthdate' in jsonentry:
                item['birthday'] = jsonentry['Birthdate']
            else:
                item['birthday'] = ''

            if 'Born' in jsonentry:
                item['birthplace'] = jsonentry['Born']
            else:
                item['birthplace'] = ''

            if 'Ethnicity' in jsonentry:
                item['ethnicity'] = jsonentry['Ethnicity']
            else:
                item['ethnicity'] = ''

            if 'Hair' in jsonentry:
                item['haircolor'] = jsonentry['Hair']
            else:
                item['haircolor'] = ''

            if 'Eyes' in jsonentry:
                item['eyecolor'] = jsonentry['Eyes']
            else:
                item['eyecolor'] = ''

            if 'Weight' in jsonentry:
                item['weight'] = jsonentry['Weight']
            else:
                item['weight'] = ''

            if item['weight']:
                item['weight'] = str(item['weight']) + "lbs"

            if 'Height' in jsonentry:
                item['height'] = jsonentry['Height']
            else:
                item['height'] = ''

            if 'Measurements' in jsonentry:
                item['measurements'] = jsonentry['Measurements']
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
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if self.debug:
                print(item)
            else:
                yield item

            item.clear()
