import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBananaFeverSpider(BaseSceneScraper):
    name = 'BananaFever'
    network = 'Banana Fever'
    parent = 'Banana Fever'
    site = 'Banana Fever'

    start_urls = [
        'https://internal-api.bananafever.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=%s&language=en',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = json.loads(response.text)
        for movie in scenes['videos']:
            item = self.init_scene()

            item['id'] = movie['video_id']

            item['title'] = movie['title']

            item['performers'] = []
            for performer in movie['talents']:
                item['performers'].append(performer['talent_name'])

            item['image'] = movie['thumbnail_url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['date'] = movie['publish_date']

            item['url'] = f"https://www.bananafever.com/video/{item['id']}"

            item['site'] = "Banana Fever"
            item['network'] = "Banana Fever"
            item['parent'] = "Banana Fever"

            if item['date'] > "2024-12-03":
                yield self.check_item(item, self.days)
