import string
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteVurigVlaanderenPerformerSpider(BasePerformerScraper):
    name = 'VurigVlaanderenPerformer'
    start_url = 'https://vurigvlaanderen.be'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/models.json?page=%s',
    }

    base_url = 'https://vurigvlaanderen.be'

    cookies = {"name": "agecookies", "value": "true"}

    headers_json = {
        'origin': 'https://vurigvlaanderen.be',
        'referer': 'https://vurigvlaanderen.be/',
        'Credentials': 'Syserauth 3-585d92b35321e910bc1c25b734531c9adf52e2679c0d42aefad09e2556cde47f-65be7945',
    }

    def get_next_page_url(self, base, page):
        url = 'https://api.sysero.nl/models?page={}&count=16&include=images:types(square):limit(1|0),products,categories&filter[status]=published&sort[published_at]=DESC&video_images=thumb&frontend=3'
        return self.format_url(base, url.format(page))

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://vurigvlaanderen.be/modellen"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        link = self.get_next_page_url(self.base_url, meta['page'])
        yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers_json)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.get_performers, meta=meta, headers=self.headers_json)

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['data']
        for performer in jsondata:
            performer = performer['attributes']
            item = PerformerItem()

            item['name'] = performer['title']
            item['image'] = f"https://cdndo.sysero.nl{performer['images']['square'][0]['path']}"
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = "Female"
            item['astrology'] = ''
            if 'birth_date' in performer and (performer['birth_date'] and performer['birth_date'] < "2006-01-01"):
                item['birthday'] = performer['birth_date']
            else:
                item['birthday'] = ''

            item['birthplace'] = string.capwords(GoogleTranslator(source='nl', target='en').translate(performer['county']))
            item['measurements'] = ''
            item['cupsize'] = ''

            item['ethnicity'] = ''

            item['haircolor'] = string.capwords(GoogleTranslator(source='nl', target='en').translate(performer['hair_color']))
            item['eyecolor'] = string.capwords(GoogleTranslator(source='nl', target='en').translate(performer['eye_color']))

            item['fakeboobs'] = ''
            if "length" in performer and performer['length']:
                item['height'] = performer['length'] + "cm"
            else:
                item['height'] = ''

            if "weight" in performer and performer['weight']:
                item['weight'] = performer['weight'] + "kg"
            else:
                item['weight'] = ''

            item['nationality'] = string.capwords(performer['country'])
            item['piercings'] = ''
            item['tattoos'] = ''
            item['network'] = 'Vurig Vlaanderen'
            item['url'] = f"https://vurigvlaanderen.be/modellen/{performer['slug']}"

            yield item
