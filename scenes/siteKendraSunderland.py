import re
import html
import json
import requests
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteKendraSunderlandVIPSpider(BaseSceneScraper):
    name = 'KendraSunderlandVIP'

    start_urls = [
        'https://www.kendrasunderlandvip.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/video_posts?per_page=10&page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = scene['id']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['content']['rendered'])).replace("\n", " ").strip())
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['url'] = scene['link']
            item['performers'] = ['Kendra Sunderland']
            item['tags'] = []

            item['trailer'] = ''
            item['site'] = "Kendra Sunderland"
            item['parent'] = "Kendra Sunderland"
            item['network'] = "Kendra Sunderland"
            item['type'] = 'Scene'
            meta['item'] = item

            if "wp:attachment" in scene['_links'] and scene['_links']['wp:featuredmedia'][0]['href']:
                image_url = scene['_links']['wp:featuredmedia'][0]['href']
            else:
                image_url = None

            item['image'] = None
            item['image_blob'] = None
            if image_url:
                req = requests.get(image_url)
                if req and len(req.text) > 5:
                    imagerow = json.loads(req.text)
                else:
                    imagerow = None

                if imagerow and 'guid' in imagerow:
                    if 'rendered' in imagerow['guid'] and imagerow['guid']['rendered']:
                        item['image'] = imagerow['guid']['rendered']
                        item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if "VIP" in item['title']:
                yield self.check_item(item, self.days)
