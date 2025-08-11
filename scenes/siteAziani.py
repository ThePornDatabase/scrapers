import re
import json
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAzianiSpider(BaseSceneScraper):
    name = 'Aziani'
    network = 'Aziani'
    parent = 'Aziani'
    site = 'Aziani'

    start_urls = [
        'https://aziani.com',
    ]

    cookies = {"name": "consent", "value": "true"}

    headers = {
        'X-Nats-Cms-Area-Id': "3b4c609c-6a0d-4cb9-9cce-0605f32b79ec",
        'X-Nats-Entity-Decode': 1,
        'x-nats-natscode': 'MC4wLjIuMi4wLjAuMC4wLjA',
    }

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 18)
        # ~ pagination = 'https://azianistudios.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=24&start=<PAGE>&cms_area_id=3&cms_block_id=111775&orderby=published_desc&content_type=video&status=enabled&text_search=&slug=&data_type_search=%7B%227%22:%22105%22%7D'
        link = f'https://azianistudios.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=18&start={page}&cms_area_id=3b4c609c-6a0d-4cb9-9cce-0605f32b79ec&cms_block_id=114458&orderby=published_desc&content_type=video&status=enabled&text_search='
        return link

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = f"https://www.aziani.com/videos?page={self.page}"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers)

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
            image = "https://c75c0c3063.mjedge.net" + scenethumb['fileuri'] + "?" + scenethumb['signature']
            # ~ image = "https://y2y8k2k4.ssl.hwcdn.net/" + scenethumb['fileuri'] + "?" + scenethumb['signature']
            item['image'] = image.replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*?)\?', image).group(1)
            item['trailer'] = ""

            item['date'] = scene['added_nice']

            item['url'] = f"https://aziani.com/video/{item['id']}"
            item['tags'] = []
            item['site'] = 'Aziani'
            item['performers'] = []
            directors = []
            for dataset in scene['data_types']:
                if dataset['data_type'] == 'Tags':
                    for tag in dataset['data_values']:
                        item['tags'].append(tag['name'])

                if dataset['data_type'] == 'Series':
                    if "data_values" in dataset and dataset['data_values']:
                        item['site'] = dataset['data_values'][0]['name']

                if dataset['data_type'] == 'Models' or dataset['data_type'] == 'Talent':
                    for model in dataset['data_values']:
                        item['performers'].append(model['name'])

                if dataset['data_type'] == 'Videographers':
                    for model in dataset['data_values']:
                        directors.append(model['name'])

            if directors:
                item['director'] = ",".join(directors)

            if "lengths" in scene and scene['lengths']:
                if "total" in scene['lengths'] and scene['lengths']['total']:
                    item['duration'] = scene['lengths']['total']

            item['parent'] = 'Aziani'
            item['network'] = 'Aziani'

            yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None
