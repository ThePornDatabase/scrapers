import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotGuysFuckSpider(BaseSceneScraper):
    name = 'HotGuysFuck'

    start_urls = [
        'https://api.hotguysfuck.com/api/videos?type=&page=2',
    ]

    headers = {
        "origin": "https://www.hotguysfuck.com",
        "referer": "https://www.hotguysfuck.com/",
        "site": "2",
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
        'pagination': '/api/videos?type=&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['videos']['data']
        for scene in jsondata:
            if ("id" in scene and scene['id']) and ("slug" in scene and scene['slug']):
                link = f"https://api.hotguysfuck.com/api/video?slug={scene['slug']}"
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta, headers=self.headers)

    def parse_scene(self, response):
        scene = response.json()
        item = SceneItem()
        item['title'] = self.cleanup_title(scene['video']['title'])

        item['date'] = scene['video']['dateRelease']

        if item['date'] > '2023-12-18':
            item['id'] = scene['video']['id']
        else:
            item['id'] = scene['video']['slug']

        item['description'] = self.cleanup_description(scene['video']['description'])

        item['image'] = self.format_link(response, scene['video']['mainPhoto']).replace(" ", "%20")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['trailer'] = ""

        item['url'] = f"https://www.hotguysfuck.com/video/{scene['video']['slug']}"

        item['tags'] = []
        if "tags" in scene and scene['tags']:
            for tag in scene['tags']:
                item['tags'].append(string.capwords(tag['name']))

        item['duration'] = self.duration_to_seconds(scene['video']['duration'])

        item['site'] = 'Hot Guys Fuck'
        item['parent'] = 'Hot Guys Fuck'
        item['network'] = 'Hot Guys Fuck'
        item['performers'] = []
        for model in scene['video']['models']:
            item['performers'].append(model['name'])

        yield self.check_item(item, self.days)
