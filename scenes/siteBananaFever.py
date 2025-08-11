import json
import scrapy
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
        'pagination': '/content/videos?page=%s&language=en',

        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        for movie in scenes['videos']:

            link = f"https://internal-api.bananafever.com/content/videos/{movie['slug']}?language=en"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        movie = response.json()
        item = self.init_scene()

        item['id'] = movie['video_id']
        item['title'] = movie['title']

        item['performers'] = []
        if "talents" in movie and movie['talents']:
            for performer in movie['talents']:
                item['performers'].append(performer['name'])

        item['description'] = movie['description']

        item['image'] = movie['thumbnail_url']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['date'] = movie['publish_date']

        tags = []
        item['tags'] = []
        if "categories" in movie and movie['categories']:
            for category in movie['categories']:
                tags.append(category['name'])

        for tag in tags:
            if "banana" not in tag.lower():
                item['tags'].append(tag)

        item['url'] = f"https://www.bananafever.com/video/{movie['slug']}"

        item['site'] = "Banana Fever"
        item['network'] = "Banana Fever"
        item['parent'] = "Banana Fever"

        if item['date'] > "2024-12-03":
            yield self.check_item(item, self.days)
