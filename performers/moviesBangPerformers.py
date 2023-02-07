import string
import base64
import json
import scrapy
import pycountry
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class MoviesBangPerformerSpider(BasePerformerScraper):
    name = 'BangMoviesPerformer'
    network = 'Bang'

    selector_map = {
        'external_id': 'video/(.+)'
    }

    per_page = 50

    def start_requests(self):
        if self.page:
            page = int(self.page)
        else:
            page = 0

        yield scrapy.Request(
            url='https://www.bang.com/api/search/actors/actor/_search',
            method='POST',
            headers={'Content-Type': 'application/json'},
            meta={'page': page},
            callback=self.parse,
            body=json.dumps(self.get_elastic_payload(self.per_page, 0))
        )

    def parse(self, response, **kwargs):
        # ~ print(response.text)
        performers = response.json()['hits']['hits']
        for performer in performers:
            yield self.parse_performer(performer)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            next_page = response.meta['page'] + 1
            if (next_page * self.per_page) > response.json()['hits']['total']:
                return

            print('NEXT PAGE: ' + str(next_page))
            yield scrapy.Request(
                url='https://www.bang.com/api/search/actors/actor/_search',
                method='POST',
                headers={'Content-Type': 'application/json'},
                callback=self.parse,
                meta={'page': next_page},
                body=json.dumps(self.get_elastic_payload(self.per_page, self.per_page * next_page)))

    def parse_performer(self, json):
        item = PerformerItem()
        json = json['_source']
        if json['name']:
            # ~ print ("   ")
            # ~ print(f'JSON: {json}')
            if json['birthCountry']:
                country = pycountry.countries.get(alpha_2=json['birthCountry'])
                if country:
                    json['birthCountry'] = country.name
            if json['nationality']:
                country = pycountry.countries.get(alpha_2=json['nationality'])
                if country:
                    json['nationality'] = country.name
            item['name'] = string.capwords(json['name'])
            item['network'] = 'Bang'
            encode_url = self.encode_url(json['id'])
            item['url'] = f'https://www.bang.com/pornstar/{encode_url}'
            item['image'] = f"https://i.bang.com/pornstars/{json['identifier']}.jpg"
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = None
            if json['gender'].lower() == "f":
                item['gender'] = "Female"
            if json['gender'].lower() == "m":
                item['gender'] = "Male"
            if json['gender'].lower() == "t":
                item['gender'] = "Trans"
            if 'gender' not in item:
                item['gender'] = json['gender']
            item['birthday'] = json['birthDate']
            item['astrology'] = None
            item['birthplace'] = string.capwords((json['birthCity'] + " " + json['birthCountry']).strip())
            item['ethnicity'] = string.capwords(json['ethnicity'])
            item['nationality'] = string.capwords(json['nationality'])
            item['haircolor'] = string.capwords(json['hairColor'])
            item['eyecolor'] = string.capwords(json['eyeColor'])
            if json['measurements']['height']:
                item['height'] = str(json['measurements']['height']) + "cm"
            else:
                item['height'] = None
            item['weight'] = None
            if json['measurements']['shoulder'] and json['measurements']['cupSize'] and json['measurements']['chest'] and json['measurements']['waist']:
                item['measurements'] = (str(json['measurements']['shoulder']) + json['measurements']['cupSize'] + "-" + str(json['measurements']['chest']) + "-" + str(json['measurements']['waist'])).upper()
                item['cupsize'] = (str(json['measurements']['shoulder']) + json['measurements']['cupSize']).upper()
            else:
                item['measurements'] = None
                item['cupsize'] = None
            item['tattoos'] = None
            item['piercings'] = None
            if not json['naturalBreasts']:
                item['fakeboobs'] = 'Yes'
            else:
                item['fakeboobs'] = "No"
            if item['gender'] == "Male":
                item['fakeboobs'] = None
            return item

    def get_elastic_payload(self, per_page, offset: int = 0):
        payload = {"size": per_page, "from": offset, "query": {"bool": {"must": [{"match": {"status": "ok"}}, {"range": {"videoCount": {"gt": 0}}}], "minimum_should_match": 0}}}
        return payload

    def encode_url(self, data):
        data = bytes.fromhex(data)
        data = base64.b64encode(data).decode('UTF-8')
        data = data.replace('+', '-').replace('/', '_').replace('=', ',')
        return data
