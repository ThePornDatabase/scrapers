import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAmazingFilmsSpider(BaseSceneScraper):
    name = 'AmazingFilms'
    network = 'Amazing Films'
    parent = 'Amazing Films'
    site = 'Amazing Films'

    start_urls = [
        'https://amazingfilms.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/GRuITlCLL_AgYOhmgLUnC/videos.json?order_by=publish_date&sort_by=desc&type=&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['contents']['data']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['description'] = self.cleanup_description(scene['description'])
            item['date'] = self.parse_date(re.search(r'(\d{4}/\d{2}/\d{2})', scene['publish_date']).group(1), date_formats=['%Y/%m/%d']).strftime('%Y-%m-%d')
            item['image'] = scene['trailer_screencap']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene['models']
            item['tags'] = scene['tags']
            if "seconds_duration" in scene:
                item['duration'] = scene['seconds_duration']
            else:
                item['duration'] = None
            item['trailer'] = scene['trailer_url']
            item['id'] = scene['id']
            item['url'] = f"https://amazingfilms.com/videos/{scene['slug']}"
            item['site'] = "Amazing Films"
            item['parent'] = "Amazing Films"
            item['network'] = "Amazing Films"
            item['type'] = "Scene"
            yield self.check_item(item, self.days)
