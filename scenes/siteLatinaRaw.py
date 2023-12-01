import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLatinaRawSpider(BaseSceneScraper):
    name = 'LatinaRaw'
    network = 'LatinaRaw'
    parent = 'LatinaRaw'
    site = 'LatinaRaw'

    start_urls = [
        'https://latinaraw.com',
    ]

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
        'pagination': '/videos',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = 1
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://latinaraw.com',
            'Referer': 'https://latinaraw.com/',
            'X-Nats-Cms-Area-Id': '2',
            'X-Nats-Entity-Decode': '1',
        }
        link = 'https://idsandbox.hostednats.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=100&start=0&cms_area_id=2&cms_block_id=100695&orderby=published_desc&content_type=video&status=enabled&data_type_search=%7B%22100001%22:%22163%22%7D'
        yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['sets']

        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['cms_set_id']
            title = scene['name']
            title = title.replace(" 4k", "").replace(" 4K", "").strip()
            item['title'] = self.cleanup_title(title)
            item['description'] = self.cleanup_description(scene['description'])
            item['performers'] = []
            for performer in scene['data_types']:
                if 'data_type' in performer and performer['data_type'] and performer['data_type'] == 'Models':
                    for perf_row in performer['data_values']:
                        item['performers'].append(perf_row['name'])

            item['site'] = "LatinaRaw"
            item['network'] = "LatinaRaw"
            item['parent'] = "LatinaRaw"
            item['url'] = "https://latinaraw.com/videos/" + item['id']
            item['date'] = scene['added_nice']
            item['duration'] = scene['lengths']['total']
            item['trailer'] = ''
            item['tags'] = []
            for tags in scene['data_types']:
                if 'data_type' in tags and tags['data_type'] and tags['data_type'] == 'Category':
                    for tag in tags['data_values']:
                        item['tags'].append(tag['name'])
            image_path = scene['preview_formatted']['thumb']['800-0'][0]['fileuri'].replace('\\/', '/')
            image_signature = scene['preview_formatted']['thumb']['800-0'][0]['signature']
            item['image'] = f"https://e6m7h9b8.ssl.hwcdn.net{image_path}?{image_signature}"
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield self.check_item(item, self.days)
