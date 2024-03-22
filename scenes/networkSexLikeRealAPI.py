import re
import string
import datetime
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SexLikeRealSpider(BaseSceneScraper):
    name = 'SexLikeRealAPI'
    network = 'SexLikeReal'

    start_urls = [
        'https://www.sexlikereal.com'
    ]

    selector_map = {
        'title': "//title/text()",
        'description': "//div[@class='u-mb--four u-lh--opt u-fs--fo u-fw--medium u-lw']/text()",
        'date': "//time[1]/@datetime",
        'performers': "//meta[@property='video:actor']/@content",
        'tags': "//meta[@property='video:tag']/@content",
        'external_id': '(?:scenes|shemale|gay)\\/(.+)',
        'image': '//meta[@name="twitter:image1"]/@content or //meta[@name="twitter:image2"]/@content or //meta[@name="twitter:image3"]/@content or //meta[@name="twitter:image"]/@content',
        'trailer': '',
        'pagination': '/scenes?type=premium&sort=most_recent&page=%s'
        # ~ 'pagination': '/trans/studios/transexvr?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article/div/div[contains(@class, "c-grid-ratio")]/a/@href').getall()
        for scene in scenes:
            meta['id'] = re.search(r'.*/(.*?)$', scene).group(1)
            meta['url'] = self.format_link(response, scene)
            try:
                idnum = re.search(r'(\d+)$', scene).group(1)
            except Exception:
                print(f"Failed on scene: {scene}")
            url = f"https://api.sexlikereal.com/virtualreality/video/id/{idnum}"
            print(url)
            if idnum:
                yield scrapy.Request(url, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        json = response.json()
        item = SceneItem()
        item['title'] = self.cleanup_title(json['title'])
        item['description'] = self.cleanup_description(json['description'])
        item['image'] = json['thumbnailUrl']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ''
        item['id'] = meta['id']

        item['trailer'] = ''
        if json['encodings']:
            for encoding in json['encodings']:
                if encoding['name'].lower() == 'h264':
                    encoding = encoding['videoSources']
                    item['trailer'] = encoding[0]['url']

        item['url'] = meta['url']
        item['date'] = datetime.datetime.utcfromtimestamp(json['date']).isoformat()
        item['site'] = json['paysite']['name']
        item['network'] = self.network
        item['parent'] = item['site']

        item['performers'] = []
        if 'actors' in json:
            for model in json['actors']:
                item['performers'].append(model['name'])

        item['tags'] = []
        for tag in json['categories']:
            item['tags'].append(string.capwords(tag['tag']['name']))

        item['markers'] = []
        if 'timeStamps' in json:
            if json['timeStamps']:
                for timetag in json['timeStamps']:
                    timestamp = {}
                    timestamp['name'] = self.cleanup_title(timetag['name'])
                    timestamp['start'] = str(timetag['ts'])
                    item['markers'].append(timestamp)
                    item['tags'].append(timestamp['name'])

        shortsite = re.sub(r'[^a-z0-9]', '', item['site'].lower())
        item['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(item['tags']))))
        matches = ['vr-bangers', 'vrconk', 'vrbtrans', 'vrbgay', 'sinsvr', 'realjamvr', 'baberoticavr', 'fuckpassvr', 'czechvr', 'stripzvr','badoink','realvr','kinkvr','babevr','vrcosplayx','18vr','wankzvr','vrhush','naughtyamerica']
        if not any(x in item['id'] for x in matches) and not any(x in shortsite for x in matches):
            matches = ['virtualtaboo', 'virtualrealporn', 'virtualrealtrans', 'virtualrealpassion', 'virtualrealamateur', 'realjamvr', 'only3x', 'wankzvr', 'naughtyamerica', 'vrhush', 'realitylovers']
            if not any(x in item['id'] for x in matches) and not any(x in shortsite for x in matches):
                matches = ['swallowbay', 'wankitnowvr', 'baberoticavr', 'vr-bangers', 'vrconk', 'vrbtrans', 'vrbgay', 'sinsvr', 'realjamvr', 'baberoticavr', 'stripzvr','badoink', 'slr-milfvr', 'milfvr', 'tranzvr']
                if not any(x in item['site'].lower() for x in matches) and not any(x in shortsite for x in matches):
                    yield self.check_item(item, self.days)
