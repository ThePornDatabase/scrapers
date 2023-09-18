import string
import json
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteVegasCastingCouchPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'VegasCastingCouchPerformer'

    start_urls = [
        'https://www.vegascastingcouch.com',
    ]

    def start_requests(self):
        link = 'https://www.vegascastingcouch.com/api/v1/performers?limit=200&offset=0&status=active&sort=sort&order=1&keyword=&sex=&size='
        yield scrapy.Request(link, callback=self.get_performers, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        jsondata = json.loads(response.text)
        for performer in jsondata:
            item = PerformerItem()
            item['name'] = performer['name']
            item['image'] = "https://www.vegascastingcouch.com" + performer['imageMediumPath'].replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['gender'] = string.capwords(performer['sex'])
            item['bio'] = performer['description']
            item['cupsize'] = performer['bust'].replace(" ", "")
            item['weight'] = performer['weight']
            item['height'] = performer['height']
            item['ethnicity'] = performer['ethnicity']
            item['haircolor'] = performer['hair']
            item['eyecolor'] = performer['eyes']
            item['birthplace'] = performer['hometown']
            item['network'] = "Vegas Casting Couch"
            item['birthday'] = ''
            item['astrology'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['tattoos'] = ''
            item['fakeboobs'] = ''
            item['piercings'] = ''
            item['url'] = f"https://www.vegascastingcouch.com/models/{performer['alias']}/{performer['_id']}"

            yield item
