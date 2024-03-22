import re
import json
import scrapy
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLukeHardySpider(BaseSceneScraper):
    name = 'LukeHardy'
    network = 'Luke Hardy'
    parent = 'Luke Hardy'
    site = 'Luke Hardy'

    start_urls = [
        'https://www.lukehardyxxx.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/army/videos.php?&p=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        with open('datafiles/LukeHardyPerformers.json') as perf_file:
            meta['performerlist'] = json.load(perf_file)
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        perf_list = meta['performerlist']['scenes']
        scenes = response.xpath('//div[@class="videoThumbBlock"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('./p/a/text()').get())

            sceneid = scene.xpath('.//img[contains(@src, "content")]/@alt').get()
            item['id'] = re.search(r'(\d+)', sceneid).group(1)

            item['description'] = ''




            scenethumb = scene.xpath('.//img[contains(@src, "content")]/@src')
            if scenethumb:
                scenethumb = scenethumb.get()
                item['image'] = f"https://www.lukehardyxxx.com/army/{scenethumb}"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['trailer'] = ""

            item['date'] = ''
            scenedate = scene.xpath('.//div[contains(@class, "videoDate")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            item['url'] = f"https://www.lukehardyxxx.com/army/video-{item['id']}.php"

            item['tags'] = []
            item['duration'] = None
            item['site'] = 'Luke Hardy'
            item['parent'] = 'Luke Hardy'
            item['network'] = 'Luke Hardy'

            item['performers'] = []
            title = item['title'].lower()
            for perf in perf_list:
                if perf['name'].lower() in title:
                    item['performers'].append(perf['name'])

            yield self.check_item(item, self.days)
