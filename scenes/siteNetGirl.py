import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNetGirlSpider(BaseSceneScraper):
    name = 'NetGirl'
    network = 'NetVideoGirls'
    parent = 'NetGirl'
    site = 'NetGirl'

    start_urls = [
        'https://www.netgirl.com/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):

        url = "https://www.netgirl.com/"
        yield scrapy.Request(url, callback=self.get_scenes)

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(text(), "pageProps")]/text()').get()
        jsondata = json.loads(jsondata)
        jsondata = jsondata['props']['pageProps']
        for key in jsondata:
            jsongroup = jsondata[key]
            if "year" not in key:
                for scene in jsongroup:
                    # ~ json_formatted_str = json.dumps(scene, indent=2)
                    # ~ print(json_formatted_str)

                    item = SceneItem()

                    item['network'] = 'NetVideoGirls'
                    item['parent'] = 'NetGirl'
                    item['site'] = 'NetGirl'

                    item['date'] = self.parse_date('today').isoformat()
                    item['title'] = scene['short_title']
                    item['id'] = scene['id']
                    item['url'] = 'https://www.netgirl.com/'

                    if "loading" in scene['thumb']:
                        item['image'] = f"https://cdn2.netgirl.com/images/web/{item['id']}-1-med.jpg"
                    else:
                        item['image'] = f"https://cdn2.netgirl.com/images/web/{scene['thumb']}"
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                    item['description'] = ''
                    item['performers'] = scene['pretty_models']
                    item['tags'] = ['Amateur', 'Audition']
                    item['trailer'] = ''
                    yield item
