import re
import string
import datetime as dt
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLusterySpider(BaseSceneScraper):
    name = 'Lustery'
    network = 'Lustery'

    start_url = 'https://lustery.com'

    selector_map = {
        'external_id': r'',
        'pagination': '/api/feed-item/get-items?offset=%s&type=videos',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://lustery.com/', callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildId'] = buildId.group(1)
            link = self.get_next_page_url(self.start_url, self.page)
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 10)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        meta = response.meta
        for scene in jsondata['feedItems']:
            if scene['publishAt']:
                meta['date'] = dt.datetime.utcfromtimestamp(scene['publishAt']).strftime('%Y-%m-%dT%H:%M:%S.%f%z')
            else:
                meta['date'] = None
            if scene['videoPermalink']:
                meta['id'] = scene['videoPermalink']
                link = f"https://lustery.com/_next/data/{meta['buildId']}/video/{meta['id']}.json?permalink={meta['id']}"
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['pageProps']
        item = SceneItem()
        item['id'] = meta['id']
        item['date'] = meta['date']
        item['url'] = f"https://lustery.com/video-preview/{item['id']}"

        # Items from 'video/video_id_node'
        video = jsondata['fallback'][f"video/{item['id']}"]['video']
        item['title'] = video['title']
        item['duration'] = video['duration']
        item['tags'] = video['tags']
        item['tags'] = item['tags'] = list(map(lambda x: string.capwords(x.replace("-", " ").strip()), item['tags']))
        item['image'] = f"https://lustery.com/{video['posterFullPath']}"
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        performers = video['coupleName']
        if "&" in performers:
            item['performers'] = performers.split("&")
        else:
            item['performers'] = [performers]
        item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

        # Items from 'video/video_id_node/info'
        info = jsondata['fallback'][f"video/{item['id']}/info"]['videoInfo']
        item['description'] = info['description']

        item['site'] = 'Lustery'
        item['parent'] = 'Lustery'
        item['network'] = 'Lustery'
        item['trailer'] = ''

        yield self.check_item(item, self.days)
