import re
import json
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkGhostProPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s&order_by=publish_date&sort_by=desc',
        'external_id': r'model/(.*)/'
    }

    name = 'GhostProPerformer'
    network = 'Ghost Pro'

    start_urls = [
        'https://www.creampiethais.com',
        'https://www.thaigirlswild.com',
        'https://www.creampieinasia.com',
        'https://www.asiansuckdolls.com',
        'https://www.creampiecuties.com',
        'https://www.gogobarauditions.com',
        'https://www.creamedcuties.com',
        'https://www.asiansybian.com',
        'https://www.thaipussymassage.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_performers(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']
            site = re.search(r'https://www\.(.*?)\.', response.url).group(1)

            for jsonrow in jsondata['models']['data']:
                item = PerformerItem()
                item['name'] = self.cleanup_title(jsonrow['name'])
                item['image'] = jsonrow['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['url'] = f"https://www.{site}.com/models/{jsonrow['id']}/{jsonrow['slug']}"
                item['network'] = 'Ghost Pro'
                item['astrology'] = None
                item['bio'] = None
                item['birthday'] = None

                if "location" in jsonrow:
                    item['birthplace'] = self.cleanup_text(jsonrow['location'])
                else:
                    item['birthplace'] = None

                item['eyecolor'] = None
                item['haircolor'] = None
                item['height'] = None
                item['weight'] = None

                if "thai" in site or "asia" in site:
                    item['ethnicity'] = "Asian"
                else:
                    item['ethnicity'] = None

                item['fakeboobs'] = None
                item['gender'] = 'Female'

                item['measurements'] = None
                item['cupsize'] = None
                item['nationality'] = None
                item['piercings'] = None
                item['tattoos'] = None

                yield item
