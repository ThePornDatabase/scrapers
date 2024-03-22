import re
import json
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class Site2Poles1HoleSpider(BaseSceneScraper):
    name = '2Poles1Hole'
    network = '2Poles1Hole'
    parent = '2Poles1Hole'
    site = '2Poles1Hole'

    start_urls = [
        'https://2poles1hole.com',
    ]

    cookies = {"name": "consent", "value": "true"}

    headers = {
        'X-Nats-Cms-Area-Id': 2,
        'X-Nats-Entity-Decode': 1,
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 16)
        pagination = 'https://azianistudios.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=16&start=%s&cms_area_id=2&cms_block_id=100086&orderby=published_desc&content_type=video&status=enabled&text_search='
        link = pagination % page
        return link

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://2poles1hole.com/videos"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        scenes = json.loads(response.text)
        for scene in scenes['sets']:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['name'])
            item['id'] = scene['cms_set_id']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))

            for thumb in scene['preview_formatted']['thumb']:
                scenethumb = thumb
            scenethumb = scene['preview_formatted']['thumb'][scenethumb][0]
            image = "https://y2y8k2k4.ssl.hwcdn.net/" + scenethumb['fileuri'] + "?" + scenethumb['signature']
            item['image'] = image.replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*?)\?', image).group(1)
            item['trailer'] = ""

            item['date'] = scene['added_nice']

            item['url'] = f"https://2poles1hole.com/video/{item['id']}"
            item['tags'] = []
            for dataset in scene['data_types']:
                if dataset['data_type'] == 'Tags':
                    for tag in dataset['data_values']:
                        item['tags'].append(tag['name'])

            item['duration'] = scene['lengths']['total']
            item['site'] = '2Poles1Hole'
            item['parent'] = '2Poles1Hole'
            item['network'] = '2Poles1Hole'
            item['performers'] = []
            for dataset in scene['data_types']:
                if dataset['data_type'] == 'Models':
                    for model in dataset['data_values']:
                        item['performers'].append(model['name'])

            yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None
