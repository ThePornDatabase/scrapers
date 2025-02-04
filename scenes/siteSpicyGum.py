import re
import urllib.parse
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSpicyGumSpider(BaseSceneScraper):
    name = 'SpicyGum'
    site = 'SpicyGum'
    parent = 'SpicyGum'
    network = 'SpicyGum'

    start_urls = [
        'https://api.spicy-gum.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?infiniteScroll=%s&order_by_column=created_at&order_by_direction=desc',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.json()
        scenes = scenes['data']
        for scene in scenes:
            scene = f"https://api.spicy-gum.com/video/{scene['slug']}"
            if scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = response.json()
        scene = scene['data']
        item = SceneItem()
        item['title'] = scene['name']
        item['description'] = scene['description']
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['created_at']).group(1)

        item['image'] = scene['thumbnail']
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image_blob'] = ''

        item['id'] = scene['id']
        item['trailer'] = ""
        item['duration'] = str(scene['duration'])
        item['url'] = f"https://spicy-gum.com/video/{urllib.parse.quote_plus(scene['slug'])}"
        item['network'] = "SpicyGum"
        item['site'] = "SpicyGum"
        item['parent'] = "SpicyGum"

        item['performers'] = []
        item['performers_data'] = []
        for star in scene['stars']:
            if "others" not in star['name'].lower():
                item['performers'].append(star['name'])
                performer_extra = {}
                performer_extra['name'] = star['name']
                performer_extra['extras'] = {}
                performer_extra['extras']['gender'] = "Female"
                perf_image = star['cover_image']
                if perf_image:
                    performer_extra['image'] = perf_image
                    performer_extra['image_blob'] = self.get_image_blob_from_link(performer_extra['image'])
                    if "?" in performer_extra['image']:
                        performer_extra['image'] = re.search(r'(.*?)\?', performer_extra['image']).group(1)
                item['performers_data'].append(performer_extra)

        item['tags'] = []
        for category in scene['categories']:
            item['tags'].append(category['name'])

        if "?" in item['image']:
            item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        yield self.check_item(item, self.days)
