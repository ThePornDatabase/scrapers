import json
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class PornboxSpider(BaseSceneScraper):
    name = 'Pornbox'
    network = 'Pornbox'
    parent = 'Pornbox'

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    start_urls = [
        'https://pornbox.com/',
    ]

    studios = [
        {'studio': 144, 'site': 'Culioneros'}
    ]

    content_json_url = 'https://pornbox.com/contents/%s'
    content_url = 'https://pornbox.com/application/watch-page/%s'

    selector_map = {
        'external_id': r'\/([0-9]+)',
        'pagination': 'studio/%s?skip=%s&sort=latest',
        'type': 'Scene',
    }

    def start_requests(self):
        for studio in self.studios:
            meta = {}
            meta['site'] = studio['site']
            meta['studio'] = studio['studio']
            meta['page'] = self.page
            url = self.get_next_page_url('https://pornbox.com/', self.page, meta)

            yield scrapy.Request(url=url,
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, meta):
        return self.format_url(base, self.get_selector_map('pagination') % (meta['studio'], page))

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        scenes = jsondata['contents']
        for scene in scenes:
            yield scrapy.Request(url=self.content_json_url % scene['id'],
                                 callback=self.parse_scene,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_scene(self, response):
        jsondata = json.loads(response.text)

        item = SceneItem()

        item['title'] = jsondata['scene_name']
        item['description'] = self.cleanup_description(jsondata['small_description'])
        item['site'] = response.meta['site']
        item['date'] = self.parse_date(jsondata['publish_date']).isoformat()
        item['image'] = jsondata['player_poster']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = list(map(lambda performer: string.capwords(performer['model_name'].strip()), jsondata['models'] + jsondata['male_models']))

        item['tags'] = list(map(lambda tag: string.capwords(tag['niche'].strip()), jsondata['niches']))

        item['id'] = jsondata['id']
        item['duration'] = self.duration_to_seconds(jsondata['runtime'])

        item['url'] = self.content_url % jsondata['id']
        item['network'] = self.network
        item['parent'] = self.parent
        item['type'] = 'Scene'

        for key in ['markers', 'trailer']:
            item[key] = ''

        yield self.check_item(item, self.days)
