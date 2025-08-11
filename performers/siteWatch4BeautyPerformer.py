from requests import get
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteWatch4BeautyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'Watch4BeautyPerformer'
    network = 'Watch4Beauty'

    start_urls = [
        'https://www.watch4beauty.com/api/models',
    ]

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        start_url = "https://www.watch4beauty.com/api/models"

        for link in self.start_urls:
            yield scrapy.Request(start_url, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        meta = response.meta
        performers = response.json()
        # ~ print(performers)
        for performer in performers['models']:
            perf = performers['models'][performer]
            url = f"https://www.watch4beauty.com/api/models/{perf['model_simple_nickname']}"
            yield scrapy.Request(url, callback=self.parse_performer, meta=meta)

    def parse_performer(self, response):
        perf = response.json()
        perf = perf[0]
        item = self.init_performer()
        item['name'] = perf['model_nickname']
        item['birthplace'] = perf['model_country']
        item['gender'] = "Female"
        item['nationality'] = perf['model_country']

        if "model_measures" in perf and perf['model_measures']:
            item['measurements'] = self.convert_cm_to_inches(perf['model_measures'])

        if "model_text" in perf and perf['model_text']:
            item['bio'] = perf['model_text']

        if "model_year" in perf and str(perf['model_year']) > "1970":
            item['birthday'] = f"{perf['model_year']}-01-01"

        item['image'] = f"https://mh-c75c2d6726.watch4beauty.com/production/model-{perf['model_simple_nickname']}-blank-960.jpg"
        # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['url'] = f"https://www.watch4beauty.com/models/{perf['model_simple_nickname']}"
        item['network'] = "Watch4Beauty"
        yield item

    def convert_cm_to_inches(self, cm_string):
        cm_values = cm_string.split('-')
        cm_to_inch = 2.54
        inch_values = [round(float(cm) / cm_to_inch) for cm in cm_values]
        inch_string = '-'.join(map(str, inch_values))
        return inch_string
