import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePOVPervSpider(BaseSceneScraper):
    name = 'POVPerv'
    network = 'POV Perv'
    parent = 'POV Perv'
    site = 'POV Perv'

    start_urls = [
        'https://tour.povperv.com',
    ]

    selector_map = {
        'external_id': r'scenes/(.*)',
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc'
    }

    cookies = {"close-warning": "1"}

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for jsonrow in jsondata:
                item = SceneItem()
                item['site'] = "POV Perv"
                item['parent'] = "POV Perv"
                item['network'] = "POV Perv"
                item['title'] = self.cleanup_title(jsonrow['title'])
                item['description'] = self.cleanup_text(jsonrow['description'])
                item['performers'] = jsonrow['models']
                item['date'] = self.parse_date(jsonrow['publish_date']).strftime('%Y-%m-%d')
                item['id'] = jsonrow['id']
                item['image'] = jsonrow['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = jsonrow['tags']
                item['trailer'] = jsonrow['trailer_url']
                item['url'] = f"https://tour.povperv.com//scenes/{jsonrow['slug']}"
                item['duration'] = self.duration_to_seconds(jsonrow['videos_duration'])
                item['type'] = 'Scene'

                if item['date'] > "2023-11-15":
                    yield self.check_item(item, self.days)
