import re
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMongerInAsiaPerformerSpider(BasePerformerScraper):
    name = 'MongerInAsiaPerformer'
    start_url = 'https://mongerinasia.com/'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/models.json?page=%s&order_by=name&sort_by=asc',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://mongerinasia.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

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
                item['gender'] = "Female"
            item['astrology'] = ''
            if "birthdate" in performer and performer['birthdate'] and "1969" not in performer['birthdate']:
                item['birthday'] = performer['birthdate']
            else:
                item['birthday'] = ''

            if "location" in performer and performer['location']:
                item['birthplace'] = performer['location']
            else:
                item['birthplace'] = ''

            item['measurements'] = ''
            item['cupsize'] = ''

            item['ethnicity'] = 'Asian'
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''

            if "height" in performer and performer['height']:
                item['height'] = self.get_height(performer['height'])
            else:
                item['height'] = ''

            if "weight" in performer and performer['weight']:
                item['weight'] = self.get_weight(performer['weight'])
            else:
                item['weight'] = ''

            if item['birthplace'] and "," in item['birthplace']:
                item['nationality'] = re.search(r', (.*)', item['birthplace']).group(1)
                item['nationality'] = item['nationality'].strip()
            else:
                item['nationality'] = ''

            item['piercings'] = ''
            item['tattoos'] = ''
            item['network'] = 'Monger In Asia'
            item['url'] = f"https://www.mongerinasia.com/models/{performer['slug']}"

            yield item

    def get_weight(self, weight):
        if weight:
            if "kilos" in weight.lower():
                weight = re.sub(r'[^0-9a-z]', "", weight.lower())
                weight = re.search(r'(\d+)kilo', weight).group(1)
                return weight + "kg"
        return None

    def get_height(self, height):
        height = height.replace("’", "'").replace("”", "\"")
        height = re.sub(r'[^0-9\'\"]', "", height)
        if "'" in height and '"' in height:
            height = re.search(r'(\d+\'\d+\")', height).group(1)
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
