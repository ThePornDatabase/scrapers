import re
import json
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePacopacomamaPerformerSpider(BasePerformerScraper):
    name = 'PacopacomamaPerformer'

    start_urls = [
        'https://en.pacopacomama.com',
    ]

    selector_map = {
        'pagination': '/dyn/phpauto/movie_lists/list_newest_%s.json',
        'external_id': r''
    }

    def get_next_page_url(self, base, page):
        page = (page - 1) * 50
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['Rows']
        for row in jsondata:
            for key, value in row['ActressesList'].items():
                item = PerformerItem()
                item['name'] = string.capwords(value['NameEn'])
                item['image'] = None
                item['image_blob'] = None
                item['url'] = f"https://en.pacopacomama.com/search/?a={key}"
                item['network'] = 'Pacopacomama'
                item['astrology'] = ''
                item['bio'] = ''
                item['birthday'] = ''
                item['birthplace'] = ''
                item['cupsize'] = ''
                item['ethnicity'] = 'Asian'
                item['eyecolor'] = ''
                item['fakeboobs'] = ''
                item['gender'] = 'Female'
                item['haircolor'] = ''
                item['height'] = ''
                item['measurements'] = ''
                if value['Sizes'] and value['Sizes'] != '00-00-00':
                    if re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', value['Sizes']):
                        measurements = re.search(r'(\d{2,3})-(\d{2,3})-(\d{2,3})', value['Sizes'])
                        bust = str(round(int(measurements.group(1)) / 2.54))
                        hips = str(round(int(measurements.group(2)) / 2.54))
                        waist = str(round(int(measurements.group(3)) / 2.54))
                        if bust and hips and waist:
                            item['measurements'] = bust + "-" + hips + "-" + waist
                item['nationality'] = ''
                item['piercings'] = ''
                item['tattoos'] = ''
                item['weight'] = ''
                yield item
