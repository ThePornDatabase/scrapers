import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteDireDesiresPerformerSpider(BasePerformerScraper):
    name = 'DireDesiresPerformer'
    site = "Dire Desires"
    parent = "Dire Desires"
    network = "Dire Desires"

    start_url = 'https://diredesires.com/'

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/<buildID>/models.json?page=%s&order_by=publish_date&sort_by=desc',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://diredesires.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = self.get_next_page_url(self.start_url, self.page, meta['buildID'])
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_performers(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['buildID']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, buildID):
        pagination = self.get_selector_map('pagination')
        pagination = pagination.replace("<buildID>", buildID)
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['models']['data']
        for performer in jsondata:
            item = self.init_performer()
            item['name'] = performer['name']
            item['image'] = performer['thumb'].replace(" ", "%20")
            # ~ item['image_blob'] = self.get_image_blob_from_link(performer['thumb'])
            item['gender'] = performer['gender']
            if 'Birthdate' in performer and performer['Birthdate']:
                item['birthday'] = performer['Birthdate']
            if 'Eyes' in performer and performer['Eyes']:
                item['eyecolor'] = performer['Eyes']
            if 'Hair' in performer and performer['Hair']:
                item['haircolor'] = performer['Hair']
            if 'Born' in performer and performer['Born']:
                item['birthplace'] = performer['Born']
            if 'Weight' in performer and performer['Weight']:
                weight = performer['Weight']
                weight = re.search(r'(\d+)', weight)
                if weight:
                    item['weight'] = str(int(int(weight.group(1)) * .453592)) + "kg"
            if 'Height' in performer and performer['Height']:
                item['height'] = self.get_height(performer['Height'])
            if 'Measurements' in performer and performer['Measurements']:
                item['measurements'] = performer['Measurements']
            item['url'] = f"https://www.diredesires.com/models/{performer['slug']}"
            item['network'] = "Dire Desires"
            yield item

    def get_height(self, height):
        if height:
            height = re.sub(r'[^0-9\']+', '', height)
            height = re.search(r'(\d+?\'\d+)', height)
            if height:
                height = height.group(1)
                tot_inches = 0
                if re.search(r'(\d+)[\'\"]', height):
                    feet = re.search(r'(\d+)\'', height)
                    if feet:
                        feet = feet.group(1)
                        tot_inches = tot_inches + (int(feet) * 12)
                    inches = re.search(r'\d+?\'(\d+)', height)
                    if inches:
                        inches = inches.group(1)
                        inches = int(inches)
                        tot_inches = tot_inches + inches
                    height = str(int(tot_inches * 2.54)) + "cm"
                    return height
        return None
