import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePowershotzSpider(BaseSceneScraper):
    name = 'Powershotz'

    start_urls = [
        'https://powershotz.com/videos',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://powershotz.com', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = f"https://powershotz.com/_next/data/{meta['buildID']}/videos.json?order_by=publish_date&sort_by=desc"
            yield scrapy.Request(link, callback=self.parse_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['pageProps']['videos']
        for scene in jsondata:
            meta['id'] = scene['id']
            link = f"https://powershotz.com/_next/data/{meta['buildID']}/{meta['id']}.json?id={meta['id']}"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.json()
        scene = jsondata['pageProps']
        item = SceneItem()
        item['title'] = self.cleanup_title(scene['product']['title'])
        item['description'] = self.cleanup_description(scene['product']['description'])
        item['date'] = ""
        item['image'] = scene['imageLink']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = []
        for model in scene['starsInData']:
            item['performers'].append(model['model_name'])
        item['tags'] = ['Bondage', 'BDSM', 'Roleplay']
        item['duration'] = None
        item['trailer'] = ""
        item['id'] = scene['product']['id']
        item['url'] = f"https://powershotz.com/{item['id']}"
        item['site'] = "Powershotz"
        item['parent'] = "Powershotz"
        item['network'] = "Powershotz"
        item['type'] = "Scene"
        yield self.check_item(item, self.days)
