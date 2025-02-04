import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFFProductionsSpider(BaseSceneScraper):
    name = 'FFProductions'

    start_urls = [
        'https://e3c2bc4a-f2c8-49a6-810e-19fcce4d6a9e.mysimplestore.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/v2/products?page_fallback=true&app=vnext&page=<PAGE>&per_page=15&q%5Bdescend_by_created_at%5D=true',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination').replace("<PAGE>", str(page)))

    def get_scenes(self, response):
        scenes = response.json()
        scenes = scenes['products']
        for scene in scenes:
            item = self.init_scene()
            item['id'] = scene['id']
            item['title'] = self.cleanup_title(scene['name'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['created_at']).group(1)
            image = scene['default_asset_url']
            if image:
                if "https:" not in image:
                    image = "https:" + image
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
            item['url'] = f"https://ffproductions.net/{scene['relative_url']}"
            item['site'] = 'FFProductions'
            item['parent'] = 'FFProductions'
            item['network'] = 'FFProductions'
            item['type'] = "Scene"

            if 'description_raw' in scene and scene['description_raw']:
                desctext = scene['description_raw']
                desctext = desctext.replace('\\"', '"').strip()
                try:
                    desctext = json.loads(desctext)
                    if desctext:
                        for desc_row in desctext['blocks']:
                            if "minutes" in desc_row['text'].lower():
                                duration = re.search(r'(\d+)', desc_row['text'])
                                if duration:
                                    item['duration'] = str(int(duration.group(1)) * 60)
                            else:
                                if desc_row['text']:
                                    item['description'] = item['description'] + desc_row['text'] + "\n"
                except:
                    print(f"Invalid JSON: {desctext}")

            yield self.check_item(item, self.days)
