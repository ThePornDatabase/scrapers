import re
import html
import json
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHucowsJSONSpider(BaseSceneScraper):
    name = 'HucowsJSON'
    network = 'Hucows'
    parent = 'Hucows'
    site = 'Hucows'

    start_urls = [
        'https://www.hucows.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/posts?per_page=10&page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = scene['slug']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['content']['rendered'])).replace("\n", " ").strip())
            item['date'] = scene['date']
            item['url'] = scene['link']
            item['performers'] = scene['yoast_head_json']['schema']['@graph'][0]['keywords']
            item['tags'] = scene['yoast_head_json']['schema']['@graph'][0]['articleSection']
            item['image'] = ''
            if "jetpack_featured_media_url" in scene:
                if scene['jetpack_featured_media_url']:
                    item['image'] = scene['jetpack_featured_media_url']
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if not item['image']:
                item['image'] = scene['yoast_head_json']['og_image'][0]['url']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ''
            item['site'] = "Hucows"
            item['parent'] = "Hucows"
            item['network'] = "Hucows"
            item['type'] = 'Scene'
            meta['item'] = item

            yield self.check_item(item, self.days)
