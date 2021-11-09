import json

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteFemJoyPerformerSpider(BasePerformerScraper):
    name = 'FemJoyPerformer'
    network = 'FemJoy'

    start_urls = {
        'https://femjoy.com/',
    }

    selector_map = {
        'external_id': r'updates/(.*)\.html$',
        'pagination': '/api/v2/actors?sorting=date&thumb_size=355x475&limit=48&page={}'
    }

    def get_performers(self, response):
        global json
        jsondata = json.loads(response.text)
        data = jsondata['results']
        for jsonentry in data:
            item = PerformerItem()

            item['name'] = jsonentry['name']
            item['image'] = jsonentry['thumb']['image']
            item['image_blob'] = None
            item['url'] = "https://femjoy.com" + jsonentry['url']

            if jsonentry['astrology']:
                item['astrology'] = jsonentry['astrology'].title()
            else:
                item['astrology'] = ''

            item['bio'] = ''
            item['birthday'] = jsonentry['birth_date']

            if jsonentry['birth_place']['name']['name']:
                item['birthplace'] = jsonentry['birth_place']['name']['name'].title()
            else:
                item['birthplace'] = ''

            if jsonentry['cup_size']:
                item['cupsize'] = jsonentry['cup_size'].upper()
            else:
                item['cupsize'] = ''

            if jsonentry['ethnicity']:
                item['ethnicity'] = jsonentry['ethnicity'].title()
            else:
                item['ethnicity'] = ''

            if jsonentry['eye_color']:
                item['eyecolor'] = jsonentry['eye_color'].title()
            else:
                item['eyecolor'] = ''

            if jsonentry['hair_color']:
                item['haircolor'] = jsonentry['hair_color'].title()
            else:
                item['haircolor'] = ''

            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['height'] = jsonentry['height']
            if jsonentry['chest'] and jsonentry['chest'] and jsonentry['waist']:
                item['measurements'] = jsonentry['chest'] + jsonentry['cup_size'] + "-" + jsonentry['waist'] + "-" + jsonentry['hip']
            else:
                item['measurements'] = ''

            if jsonentry['nationality']:
                item['nationality'] = jsonentry['nationality'].title()
            else:
                item['nationality'] = ''

            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = jsonentry['weight']
            item['network'] = 'FemJoy'

            if self.debug:
                print(item)
            else:
                yield item

            item.clear()

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination').format(page))
        return url
