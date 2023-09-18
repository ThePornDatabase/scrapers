import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNickMarxxSpider(BaseSceneScraper):
    name = 'NickMarxx'
    network = 'Nick Marxx'
    parent = 'Nick Marxx'
    site = 'Nick Marxx'

    start_urls = [
        'https://nickmarxx.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/_next/data/yNVtcdCdptanZRC611BR8/videos.json?order_by=publish_date&sort_by=desc&type=&page=%s',
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
            item['image'] = scene['thumb']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene['models']
            item['tags'] = scene['tags']
            if "seconds_duration" in scene:
                item['duration'] = scene['seconds_duration']
            else:
                item['duration'] = None
            item['trailer'] = scene['trailer_url']
            item['id'] = scene['id']
            item['url'] = f"https://nickmarxx.com/videos/{scene['slug']}"
            item['site'] = "Nick Marxx"
            item['parent'] = "Nick Marxx"
            item['network'] = "Nick Marxx"
            item['type'] = "Scene"
            yield self.check_item(item, self.days)
