import json
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class Site1PondoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = '1PondoPerformer'
    network = '1Pondo'

    start_urls = [
        'https://en.1pondo.tv',
    ]

    def get_gender(self, response):
        return 'Female'

    def start_requests(self):
        urls = {
            "https://en.1pondo.tv/dyn/phpauto/actresses_en.json",
            "https://www.10musume.com/dyn/phpauto/actresses_en.json"
        }
        for url in urls:
            yield scrapy.Request(url, callback=self.get_performers, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        jsondata = json.loads(response.text)
        for value in jsondata:
            performers = jsondata[value][value]
            for performer in performers:
                item = PerformerItem()

                item['name'] = self.cleanup_title(performer['name'])
                if performer['image_url']:
                    item['image'] = self.format_link(response, performer['image_url'])
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image'] = None
                    item['image_blob'] = None
                item['bio'] = ''
                item['gender'] = 'Female'
                item['astrology'] = ''
                item['birthday'] = ''
                item['birthplace'] = ''
                item['cupsize'] = ''
                item['ethnicity'] = 'Asian'
                item['eyecolor'] = ''
                item['fakeboobs'] = ''
                item['haircolor'] = ''
                item['height'] = ''
                item['measurements'] = ''
                item['nationality'] = ''
                item['piercings'] = ''
                item['tattoos'] = ''
                item['weight'] = ''
                item['network'] = 'D2Pass'
                if "pondo" in response.url:
                    item['url'] = f"https://en.1pondo.tv/search/?a={performer['id']}"
                if "musume" in response.url:
                    item['url'] = f"https://www.10musume.com/search/?a={performer['id']}"
                # ~ print(item)
                yield item
