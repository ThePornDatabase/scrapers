import re
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteFreakMobMediaPerformerSpider(BasePerformerScraper):
    name = 'FreakMobMediaPerformer'
    start_url = 'https://freakmobmedia.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/models.json?page=%s&order_by=publish_date&sort_by=desc',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://freakmobmedia.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = self.get_next_page_url(self.start_url, self.page, meta['buildID'])
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, buildID):
        pagination = self.get_selector_map('pagination')
        pagination = pagination.replace("<buildID>", buildID)
        return self.format_url(base, pagination % page)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['buildID']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
            item['network'] = 'Freak Mob Media'
            item['url'] = f"https://freakmobmedia.com/models/{performer['slug']}"

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
