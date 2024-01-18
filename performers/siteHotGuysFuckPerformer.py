import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteHotGuysFuckPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/api/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'HotGuysFuckPerformer'
    network = 'Hot Guys Fuck'

    start_urls = [
        'https://api.hotguysfuck.com',
    ]

    headers = {
        "origin": "https://www.hotguysfuck.com",
        "referer": "https://www.hotguysfuck.com/",
        "site": "2",
    }

    def get_performers(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['models']['data']
        for model in jsondata:
            if ('isModel' in model and model['isModel']):
                meta['slug'] = model['slug']
                link = f"https://api.hotguysfuck.com/api/profile?slug={model['slug']}&isModelRoute=1"
                yield scrapy.Request(link, callback=self.parse_performer, meta=meta, headers=self.headers)

    def parse_performer(self, response):
        meta = response.meta
        model = response.json()
        model['slug'] = meta['slug']
        item = PerformerItem()
        item['name'] = string.capwords(model['profileName'])
        item['image'] = self.format_link(response, model['squareAvatar'])
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['url'] = f"https://www.hotguysfuck.com/model/{model['slug']}"

        item['network'] = 'Hot Guys Fuck'
        if "info" in model and "sign" in model['info']:
            item['astrology'] = model['info']['sign']
        else:
            item['astrology'] = ''

        if "aboutMe" in model and model['aboutMe']:
            item['bio'] = self.cleanup_description(model['aboutMe'])
        else:
            item['bio'] = ''

        item['birthday'] = ''
        if "location" in model and model['location']:
            item['birthplace'] = model['location']
        else:
            item['birthplace'] = ''

        item['measurements'] = ''

        if "physic" in model and "breast" in model['physic']:
            item['cupsize'] = model['physic']['breast']
        else:
            item['cupsize'] = ''

        item['eyecolor'] = ''
        item['haircolor'] = ''

        item['height'] = None
        if "physic" in model and "heightData" in model['physic']:
            if "feet" in model['physic']['heightData'] and model['physic']['heightData']['feet']:
                feet = int(model['physic']['heightData']['feet']) * 30.48
                if "inches" in model['physic']['heightData'] and model['physic']['heightData']['inches']:
                    inches = int(model['physic']['heightData']['inches']) * 2.54
                else:
                    inches = 0
                if feet and inches:
                    item['height'] = str(int(feet + inches)) + "cm"

        item['weight'] = None
        if "physic" in model and "weight" in model['physic']:
            weight = model['physic']['weight']
            if weight:
                item['weight'] = str(int(int(weight) / 2.205)) + "kg"

        if "physic" in model and "sexString" in model['physic']:
            item['gender'] = string.capwords(model['physic']['sexString'])
        else:
            item['gender'] = None

        item['ethnicity'] = ''
        item['fakeboobs'] = ''
        item['nationality'] = ''
        item['piercings'] = ''
        item['tattoos'] = ''
        yield item
