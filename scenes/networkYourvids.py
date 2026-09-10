import re
from cleantext import clean
from requests import get
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkYourvidsSpider(BaseSceneScraper):
    name = 'Yourvids'

    start_urls = [
        'https://yourvids.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/videos?page=<PAGE>&perPage=40&sortBy=newest',
        'type': 'Scene',
    }

    async def start(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1:
            self.limit_pages = 10        

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination')
        return self.format_url(base, pagination.replace("<PAGE>", str(page)))
    
    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.json()
        scenes = scenes['data']['videos']

        for scene in scenes:
            item = self.init_scene()
            item['title'] = string.capwords(clean(scene['title'], no_emoji=True))
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['created_at']).group(1)

            item['image'] = scene['thumbnail']
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image_blob'] = ''

            item['id'] = scene['id']
            item['duration'] = self.duration_to_seconds(scene['duration'])
            item['url'] = scene['video_url']
            item['network'] = "Yourvids"
            item['site'] = f"Yourvids: {scene['creator_name']}"
            item['parent'] = "Yourvids"

            item['performers'] = [scene['creator_name']]
            item['performers_data'] = []
            perf = {}
            perf['name'] = scene['creator_name']
            perf['url'] = scene['creator_url']
            perf['extra'] = {}
            # perf['extra']['gender'] = "Female"
            perf['network'] = "Yourvids"
            perf['site'] = item['site']
            perf['image'] = scene['profile_image']
            perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
            item['performers_data'].append(perf)
            
            yield self.check_item(item, self.days)
