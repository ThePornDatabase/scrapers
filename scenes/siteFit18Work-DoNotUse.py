import scrapy
import re
import json
from scrapy.http import Request
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFit18WorkSpider(BaseSceneScraper):
    name = 'Fit18Work'

    network = "Fit18"

    start_urls = [
        'https://fit18.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.xpath('//script[contains(text(), "INITIAL__DATA")]/text()').get()
        jsondata = jsondata.replace('\\"', '"')
        jsondata = re.search(r'(\{.*\})', jsondata).group(1)
        jsondata = json.loads(jsondata)
        jsondata_str = json.dumps(jsondata, indent=2)
        jsondata = jsondata['page']['current']['recent']
        for jsonrow in jsondata:

            item = SceneItem()
            sceneid = jsonrow['videoId']
            item['id'] = sceneid.replace(":", "-")
            item['title'] = self.cleanup_title(jsonrow['title'])
            item['description'] = self.cleanup_description(jsonrow['description']['long'])
            item['performers'] = []
            for performer in jsonrow['talent']:
                item['performers'].append(performer['talent']['name'])

            item['site'] = "Fit 18"
            item['network'] = "Fit 18"
            item['parent'] = "Fit 18"
            item['url'] = "https://fit18.com/videos/" + sceneid.replace(':', '%3A')
            item['date'] = self.parse_date('today').strftime('%Y-%m-%d')
            item['trailer'] = ''
            item['tags'] = []
            item['image'] = jsonrow['homeImage']['landscape']['x1']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield item
