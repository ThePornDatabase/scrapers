import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class BabestationSpider(BaseSceneScraper):
    name = 'Babestation'
    site = 'Babestation'

    start_urls = [
        'https://www.babestation.tv'
    ]
    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Inertia': 'true',
        'X-Inertia-Version': '8acbe0013dae039edff7794c060c6c88'

    }
    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/video/vip-previews/page/%s',
    }

    limit_pages = 500

    def get_scenes(self, response):
        # print(response.body)
        movies = response.json()['props']['previews']
        print (len(movies))
        for movie in movies:
            url = '/'.join(['https://www.babestation.tv/video/vip-previews/watch', str(movie['id']),movie['slug']])
            yield scrapy.Request(url=url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies)
        response.meta['page'] = response.json()['props']['pagination']['currentPage']

    def parse_scene(self, response):
        movie = response.json()['props']['video']
        item = SceneItem()
        item['id'] = movie['id']
        item['title'] = movie['title']
        item['description'] = movie['description']
        item['performers'] = [k['name'] for k in movie['bs_models']]

        item['duration'] = movie['duration']


        item['date'] = self.parse_date(movie['publish_date']).isoformat()
        item['tags'] = [k['name'] for k in movie['tags']]
        item['trailer'] = movie['vip_preview']

        item['site'] = item['network'] = item['parent'] = self.site
        item['url'] = response.url

        item['image'] = movie['main_thumbnail']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        yield self.check_item(item, self.days)
