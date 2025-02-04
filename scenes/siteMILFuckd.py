import re
import requests
import json
import unidecode
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMILFuckdSpider(BaseSceneScraper):
    name = 'MILFuckd'
    network = 'MILFuckd'
    parent = 'MILFuckd'
    site = 'MILFuckd'

    start_urls = [
        'https://milfuckd.com',
    ]

    selector_map = {
        'image': '',
        'performers': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/videos?page=%s&per_page=10',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        categories = requests.get('https://milfuckd.com/wp-json/wp/v2/video-categories?page=1&per_page=100')
        if categories:
            meta['categories'] = json.loads(categories.content.decode('utf8'))

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        for scene in scenes:
            item = self.init_scene()
            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = scene['title']['rendered']
            item['url'] = scene['link']
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['content']['rendered'])).replace("\n", " ").strip())
            item['tags'] = []
            if "video-categories" in scene and scene['video-categories']:
                for category in scene['video-categories']:
                    for videocat in meta['categories']:
                        if category == videocat['id']:
                            item['tags'].append(videocat['name'])
            item['site'] = 'MILFuckd'
            item['parent'] = 'MILFuckd'
            item['network'] = 'MILFuckd'

            meta['item'] = item.copy()

            yield scrapy.Request(item['url'], callback=self.scene_parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def scene_parse(self, response):
        meta = response.meta
        item = meta['item']

        trailer = response.xpath('//video/@src')
        if trailer:
            item['trailer'] = self.format_link(response, trailer.get())

        image = response.xpath('//div[contains(@class, "image-overlay")]/@style')
        if image:
            image = re.search(r'(http.*?)\)', image.get())
            if image:
                item['image'] = image.group(1)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        performers = response.xpath('//a[contains(@href, "/performers/")]/ancestor::div[contains(@class, "e-parent")][1]//h5/text()')
        if performers:
            item['performers'] = performers.getall()

        if self.check_item(item, self.days):
            yield item
