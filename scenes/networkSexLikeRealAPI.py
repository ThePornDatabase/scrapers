import re
from requests import get
import string
import datetime
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SexLikeRealSpider(BaseSceneScraper):
    name = 'SexLikeRealAPI'
    network = 'SexLikeReal'

    start_urls = [
        'https://api.sexlikereal.com'
    ]

    headers = {"client-type": "web"}

    selector_map = {
        'title': "//title/text()",
        'description': "//div[@class='u-mb--four u-lh--opt u-fs--fo u-fw--medium u-lw']/text()",
        'date': "//time[1]/@datetime",
        'performers': "//meta[@property='video:actor']/@content",
        'tags': "//meta[@property='video:tag']/@content",
        'external_id': '(?:scenes|shemale|gay)\\/(.+)',
        'image': '//meta[@name="twitter:image1"]/@content or //meta[@name="twitter:image2"]/@content or //meta[@name="twitter:image3"]/@content or //meta[@name="twitter:image"]/@content',
        'trailer': '',
        # ~ 'pagination': '/scenes?type`=premium&sort=most_recent&page=%s'
        'pagination': '/v3/scenes?page=%s&perPage=24&sort=recent&type=new'
        # ~ 'pagination': '/trans/studios/transexvr?page=%s'
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1 and self.page == 1:
            self.limit_pages = 25

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        meta = response.meta
        json = response.json()
        for scene in json['data']:
            meta['id'] = scene['id']
            url = f"https://api.sexlikereal.com/v3/scenes/{scene['label']}"
            if meta['id']:
                yield scrapy.Request(url, callback=self.parse_scene, meta=meta, headers=self.headers)

    def parse_scene(self, response):
        meta = response.meta
        scene = response.json()
        scene = scene['data']
        item = self.init_scene()

        item['title'] = self.cleanup_title(scene['title'])
        item['date'] = datetime.datetime.utcfromtimestamp(scene['date']).strftime('%Y-%m-%d')
        if self.check_item(item, self.days):
            if "description" in scene and scene['description']:
                item['description'] = self.cleanup_description(scene['description'])

            item['image'] = scene['thumbnailUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = str(meta['id'])

            if "videoPreview" in scene and scene['videoPreview']:
                item['trailer'] = scene['videoPreview']

            item['url'] = f"https://www.sexlikereal.com/scenes/{scene['label']}"
            item['site'] = scene['studio']['name']
            item['network'] = item['site']
            item['parent'] = item['site']

            item['performers'] = []
            if 'actors' in scene:
                for model in scene['actors']:
                    item['performers'].append(model['name'])

            item['tags'] = []
            for tag in scene['categories']:
                item['tags'].append(string.capwords(tag['name']))

            item['markers'] = []
            if 'timestamps' in scene:
                if scene['timestamps']:
                    for timetag in scene['timestamps']:
                        timestamp = {}
                        timestamp['name'] = self.cleanup_title(timetag['name'])
                        timestamp['start'] = str(timetag['timestamp'])
                        item['markers'].append(timestamp)
                        item['tags'].append(timestamp['name'])
            item['tags'].append("Virtual Reality")

            item['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(item['tags']))))

            shortsite = re.sub(r'[^a-z0-9]', '', item['site'].lower())
            raw_matches = ['18vr', 'arporn', 'babevr', 'baberoticavr', 'badoink', 'blowvr', 'czechvr', 'fuckpassvr', 'girlsway',
                        'joibabes', 'kinkvr', 'milfvr', 'naughtyamerica', 'only3x', 'passionsonly', 'peterskingdom', 'porncorn',
                        'porncornvr', 'povmasters', 'puretaboo', 'realjamvr', 'realvr', 'realitylovers', 'sinsvr', 'slrmilfvr',
                        'stripzvr', 'swallowbay', 'tranzvr', 'vrcosplayx', 'vrbangers', 'vrbgay', 'vrbtrans',
                        'vrconk', 'vrhush', 'vrlatina', 'virtualrealamateur', 'virtualrealpassion', 'virtualrealporn',
                        'virtualrealtrans', 'virtualtaboo', 'wankitnowvr', 'wankzvr']

            matches = [re.sub(r'[^a-z0-9]', '', x) for x in raw_matches]

            if not any(x in shortsite for x in matches):
                yield self.check_item(item, self.days)
