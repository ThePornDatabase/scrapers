import datetime
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHAnimeSpider(BaseSceneScraper):
    name = 'HAnime'

    headers = {
        'Referer': 'https://hanime.tv/',
        'Origin': 'https://hanime.tv',
        }

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        
        meta = {}
        link = 'https://cached.freeanimehentai.net/api/v10/search_hvs'
        yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = response.json()
        for scene in jsondata:
            item = self.init_scene()
            item['date'] = datetime.datetime.utcfromtimestamp(scene['created_at']).strftime("%Y-%m-%d")
            if self.check_item(item, self.days):
                item['id'] = scene['id']
                item['title'] = string.capwords(self.cleanup_title(scene['name']))
                item['description'] = self.cleanup_description(scene['description'])
                item['date'] = datetime.datetime.utcfromtimestamp(scene['released_at']).strftime("%Y-%m-%d")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), scene['tags']))
                item['tags'].extend(['Hentai', 'Anime', 'Animated'])
                item['site'] = string.capwords(scene['brand'])
                item['parent'] = item['site']
                item['network'] = item['site']
                item['image'] = scene['poster_url']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['poster'] = scene['cover_url']
                item['poster_blob'] = self.get_image_blob_from_link(item['poster'])

                yield item