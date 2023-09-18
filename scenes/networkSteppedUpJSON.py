import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSteppedUpJSONSpider(BaseSceneScraper):
    name = 'SteppedUpJSON'
    network = 'Stepped Up'

    start_urls = [
        'https://tour.swallowed.com',
        'https://tour.nympho.com',
        'https://tour.trueanal.com',
        'https://tour.allanal.com',
        'https://tour.analonly.com',
        'https://sidechick.com',
    ]

    selector_map = {
        'external_id': r'scenes/(\d+?)/',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = SceneItem()
                item['site'] = scene['site']
                item['parent'] = scene['site']
                item['network'] = "Stepped Up"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = scene['models']
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                if "nympho" in response.url:
                    item['id'] = scene['slug']
                else:
                    item['id'] = scene['id']
                if "sidechick" in response.url:
                    item['image'] = scene['trailer_screencap'].replace(" ", "%20")
                else:
                    item['image'] = scene['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://tour.{scene['site_domain']}/scenes/{scene['slug']}"

                yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        if "sidechick" in base:
            pagination = '/videos?page=%s&order_by=publish_date&sort_by=desc'
        else:
            pagination = '/scenes?page=%s&order_by=publish_date&sort_by=desc'

        return self.format_url(base, pagination % page)
