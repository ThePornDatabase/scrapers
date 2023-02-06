import json

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class PinkyxxxSpider(BaseSceneScraper):
    name = 'PinkyXXX'

    start_urls = [
        'https://pinkyxxx.com'
    ]

    selector_map = {
        'external_id': r'preview/(.+)',
        'pagination': '/wp-admin/admin-ajax.php?action=vls&vid_type=promo&list_type=views&limit=100&offset=%s'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        for scene in jsondata['listings']:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['date'] = scene['info']['post_date']
            item['image'] = scene['poster'][0]
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['description'] = scene['description']
            item['id'] = scene['ID']
            item['trailer'] = ''
            item['tags'] = []
            item['performers'] = []
            item['url'] = scene['permalink']
            item['type'] = 'Scene'
            item['site'] = 'PinkyXXX'
            item['parent'] = 'PinkyXXX'
            item['network'] = 'PinkyXXX'
            yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 100)
        return self.format_url(base, self.get_selector_map('pagination') % page)
