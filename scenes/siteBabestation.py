import scrapy
import html
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from requests import get
true = True
false = False


class BabestationSpider(BaseSceneScraper):
    name = 'Babestation'
    site = 'Babestation X'

    start_urls = [
        'https://www.babestation.tv'
    ]

    headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Inertia': 'true',
        'X-Inertia-Version': ''
    }

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/video/vip-previews/page/%s',
    }

    async def start(self):
        start_url = 'https://www.babestation.tv/video/vip-previews/page/1'
        yield scrapy.Request(start_url, callback=self.start_requests2)

    def start_requests2(self, response):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        data_page = response.xpath('//div[@id="app"]/@data-page').get()
        if data_page:        
            json_page = json.loads(html.unescape(data_page))
            if "version" in json_page and json_page['version']:
                self.headers['X-Inertia-Version'] = json_page['version']

        for link in self.start_urls:
            url=self.get_next_page_url(link, self.page)
            yield scrapy.Request(url=url, callback=self.parse, meta=meta, headers=self.headers, dont_filter=True)    

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, dont_filter=True)

    def get_scenes(self, response):
        movies = response.json()['props']['previews']
        for movie in movies:
            url = '/'.join(['https://www.babestation.tv/video/vip-previews/watch', str(movie['id']),movie['slug']])
            yield scrapy.Request(url=url, callback=self.parse_scene, headers=self.headers, dont_filter=True)

    def parse_scene(self, response):
        movie = response.json()['props']['video']
        item = SceneItem()
        item['id'] = movie['id']
        item['title'] = movie['title']
        item['description'] = movie['description']

        models = movie.get('bs_models', [])
        if isinstance(models, dict):
            iterable = models.values()
        elif isinstance(models, list):
            iterable = models
        else:
            iterable = []

        item['performers'] = [
            m['name']
            for m in iterable
            if isinstance(m, dict) and 'name' in m
        ]

        item['duration'] = movie['duration']

        item['date'] = self.parse_date(movie['publish_date']).isoformat()
        item['tags'] = [k['name'] for k in movie['tags']]
        item['trailer'] = movie['vip_preview']

        item['site'] = item['network'] = item['parent'] = self.site
        item['url'] = response.url

        item['image'] = movie['main_thumbnail']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['image_blob'] = None
        yield self.check_item(item, self.days)
