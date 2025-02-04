import re
import requests
import codecs
from cleantext import clean
from datetime import datetime
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkSwagLiveSpider(BaseSceneScraper):
    name = 'SwagLive'
    network = 'SwagLive'
    parent = 'SwagLive'
    site = 'SwagLive'

    start_urls = [
        'https://swag.live',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/flix-categories/new_m_a?ui=flix&lang=en&page=%s',
        'type': 'Scene',
    }

    performers = [
        ["655f569788e46c0ea1102b94", "Li Rongrong", "SwagLive: Sunnyday9"],
        ["657c19caae8ed74240c80c6b", "Wei Qiaoan", "SwagLive: Weijoannana"],
        ["5f391911fc8dbc07e79531ce", "Xinxin", "SwagLive: Ezrabebe"],
        ["5c7b62ed1817b7bd43cca413", "Linlin", "SwagLive: Linlinbebe"],
        ["5a28f2f7af9c462c61546a78", "Weng Yucheng", "SwagLive: Princessdolly"],
        ["65f51e4704f60b6519345ec5", "", "SwagLive: AsiaXXXTour"],
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for performer in self.performers:
            meta['siteid'] = performer[0]
            meta['site'] = performer[2]
            meta['parent'] = "SwagLive"
            meta['performers'] = list(map(lambda x: string.capwords(x.strip()), performer[1].split(",")))
            if len(meta['performers']) == 1 and meta['performers'][0]:
                meta['performers_data'] = self.get_performers_data(meta['performers'], meta)
            else:
                meta['performers_data'] = False

            link = f"https://api.swag.live/feeds/post_video_{meta['siteid']}?filters=source:&sorting=desc:posted_at"
            yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        pagination = response.url
        meta['pagination'] = re.sub(r'page=\d+', 'page=%s', pagination.replace("limit=100", "limit=10"))
        link = meta['pagination'] % meta['page']
        yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                link = meta['pagination'] % meta['page']
                yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta

        jsondata = response.json()

        for scene in jsondata:
            meta['id'] = scene['id']
            meta['date'] = datetime.fromtimestamp(scene['createdAt']).strftime('%Y-%m-%d')
            meta['duration'] = scene['metadata']['duration']
            meta['tags'] = []
            for tag in scene['categories']:
                meta['tags'].append(string.capwords(tag.replace("_", " ")))
            meta['image'] = f"https://public.swag.live/messages/{meta['id']}/poster.jpg"
            meta['url'] = f"https://swag.live/post/{meta['id']}?lang=en"
            yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        script_text = response.xpath('//script[contains(text(), "self.__next_f.push") and contains(text(), "i18nCaption")]/text()').get()
        script_text = script_text.replace('\\"', '"')
        search_text = r'\"<ID>\"\:(\{\"created.*?\"cast\".*?\]\})'.replace("<ID>", meta['id'])
        script_text = re.search(search_text, script_text).group(1)
        script_text = script_text.replace('\\\\', '\\').replace('\n', ' ').replace('\"', '"')
        try:
            scene = json.loads(script_text)

            item = self.init_scene()
            item['id'] = meta['id']
            item['date'] = meta['date']
            item['tags'] = meta['tags']
            if meta['performers']:
                item['performers'] = meta['performers']
            else:
                item['performers'] = []

            if meta['performers_data']:
                item['performers_data'] = meta['performers_data']

            item['duration'] = meta['duration']
            item['image'] = meta['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['url'] = meta['url']
            item['site'] = meta['site']
            item['parent'] = "Swag Live"
            item['network'] = "Swag Live"
            item['type'] = "Scene"
            trailer_url = f"https://public.swag.live/messages/{meta['id']}/{scene['assetIds'][0]}/trailer.mp4"
            if self.check_url_exists(trailer_url):
                item['trailer'] = trailer_url

            item['title'] = self.cleanup_title(clean(scene['i18nTitle']['en'].replace('{username}', ' ').replace('\\\\n', ' ').replace('\\n', ' '), no_emoji=True))
            item['description'] = self.cleanup_description(clean(scene['i18nCaption']['en'].replace('{username}', ' ').replace('\\n', ' '), no_emoji=True))

            yield self.check_item(item, self.days)

        except Exception as ex:
            print(f"Exception on scene '{meta['url']}':", ex)
            print(script_text)

    def check_url_exists(self, url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return False

    def get_performers_data(self, performer_list, meta):
        performers_data = []
        if len(performer_list):
            for performer in performer_list:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Swag Live"
                perf['site'] = meta['site']
                perf['image'] = f"https://public.swag.live/users/{meta['siteid']}/picture.jpg"
                perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
                performers_data.append(perf)
        return performers_data
