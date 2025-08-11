import re
import requests
import json
import unidecode
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPKJMediaSpider(BaseSceneScraper):
    name = 'PKJMedia'
    network = 'PKJ Media'

    start_urls = [
        'https://milfuckd.com',
        'https://pervertedpov.com',
        'https://peterskingdom.com',
        'https://rawwhitemeat.com',
        'https://slutsaroundtown.com',
        'https://www.mypovfam.com',
        'https://www.passionsonly.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/videos?page=%s&per_page=10',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            categories = requests.get(f'{link}/wp-json/wp/v2/video-category?page=1&per_page=100')
            if categories:
                meta['categories'] = json.loads(categories.content.decode('utf8'))

            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        for scene in scenes:
            item = self.init_scene()
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['title'] = scene['title']['rendered']
            item['url'] = scene['link']
            item['id'] = str(scene['id'])
            item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['content']['rendered'])).replace("\n", " ").strip())
            item['tags'] = []
            if "video-category" in scene and scene['video-category']:
                for category in scene['video-category']:
                    for videocat in meta['categories']:
                        if category == videocat['id']:
                            item['tags'].append(videocat['name'])
            item['site'] = re.search(r'.*?(\w+)\.com/', response.url).group(1)
            item['parent'] = item['site']
            item['network'] = 'PKJ Media'

            meta['item'] = item.copy()

            yield scrapy.Request(item['url'], callback=self.scene_parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def scene_parse(self, response):
        meta = response.meta
        item = meta['item']

        trailer = response.xpath('//video/@src')
        if trailer:
            item['trailer'] = self.format_link(response, trailer.get())

        image = response.xpath('//video/@poster')
        if image:
            image = image.get()
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        performers = response.xpath('//span[contains(text(), "Starring:")]/a/text()')
        if performers:
            item['performers'] = performers.getall()

        if self.check_item(item, self.days):
            yield item
