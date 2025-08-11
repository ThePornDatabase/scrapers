import re
import string
from urllib.parse import urlencode
import datetime
import scrapy
from slugify import slugify
from tldextract import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ProjectOneServiceHentaiProsSpider(BaseSceneScraper):
    name = 'ProjectOneServiceHentaiPros'
    network = 'mindgeek'

    start_urls = [
        'https://www.hentaipros.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies, meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)

        headers = {
            'instance': token,
            'Origin': response.meta['url'],
            'Referer': response.meta['url'] + "/videos",
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 25
        response.meta['page'] = self.page - 1
        response.meta['url'] = response.url
        return self.get_next_page(response)

    def get_scenes(self, response):
        scene_count = 0

        for scene in response.json()['result']:
            if scene['brand'].lower().strip() in ['hentaipros', 'brazzers', 'brazzersvr']:
                item = SceneItem()
                if scene['collections'] and len(scene['collections']):
                    item['site'] = scene['collections'][0]['name']
                else:
                    item['site'] = tldextract.extract(response.meta['url']).domain

                item['image'] = self.get_image(scene)

                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['trailer'] = self.get_trailer(scene)
                if not item['trailer']:
                    item['trailer'] = ''
                item['date'] = self.parse_date(scene['dateReleased']).isoformat()
                if "letsdoeit" in response.url:
                    item['id'] = scene['spartanId']
                else:
                    item['id'] = scene['id']
                item['network'] = self.network
                item['parent'] = tldextract.extract(response.meta['url']).domain

                if 'title' in scene:
                    item['title'] = scene['title']
                else:
                    item['title'] = item['site'] + ' ' + self.parse_date(scene['dateReleased']).strftime('%b/%d/%Y')

                if 'description' in scene:
                    item['description'] = scene['description']
                else:
                    item['description'] = ''

                item['performers'] = []
                item['performers_data'] = []
                if "actors" in scene and scene['actors']:
                    for model in scene['actors']:
                        performer = string.capwords(model['name'])
                        performer_extra = {}
                        performer_extra['name'] = performer
                        performer_extra['site'] = "Mindgeek"
                        if "gender" in model and model['gender']:
                            performer_extra['extra'] = {}
                            performer_extra['extra']['gender'] = model['gender']
                        item['performers_data'].append(performer_extra)
                        item['performers'].append(performer)

                item['tags'] = []
                for tag in scene['tags']:
                    item['tags'].append(tag['name'])

                if "isVR" in scene or "virtualporn" in response.url:
                    if scene['isVR']:
                        item['tags'].append("VR")

                try:
                    item['duration'] = scene['videos']['mediabook']['length']
                except Exception:
                    item['duration'] = ''

                item['markers'] = []
                if "timeTags" in scene:
                    for timetag in scene['timeTags']:
                        timestamp = {}
                        timestamp['name'] = self.cleanup_title(timetag['name'])
                        timestamp['start'] = str(timetag['startTime'])
                        timestamp['end'] = str(timetag['endTime'])
                        item['markers'].append(timestamp)
                        scene['tags'].append(timestamp['name'])
                    item['markers'] = self.clean_markers(item['markers'])
                    item['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(item['tags']))))

                siteurl = re.compile(r'\W')
                siteurl = re.sub(siteurl, '', item['site']).lower()
                brand = scene['brand'].lower().strip()

                item['url'] = f"https://www.{brand}.com/video/{scene['id']}/{slugify(item['title'])}"

                item['parent'] = string.capwords(item['parent'])

                if "hentai" in item['site'].lower():
                    item['site'] = "HentaiPros"
                    if not item['performers']:
                        item['tags'].append('Animated')
                        item['tags'].append('Hentai')

                if self.check_item(item, self.days):
                    scene_count = scene_count + 1
                    yield item

            if scene_count > 0:
                if 'page' in response.meta and (
                        response.meta['page'] % response.meta['limit']) < self.limit_pages:
                    yield self.get_next_page(response)

    def get_next_page(self, response):
        meta = response.meta

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'adaptiveStreamingOnly': 'false',
            'dateReleased': f"<{tomorrow}",
            'orderBy': '-dateReleased',
            'type': 'scene',
            'limit': meta['limit'],
            'offset': (meta['page'] * meta['limit']),
        }
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        print('NEXT PAGE: ' + str(meta['page']))

        link = 'https://site-api.project1service.com/v2/releases?' + urlencode(query)
        return scrapy.Request(url=link, callback=self.get_scenes,
                              headers=response.meta['headers'], meta=meta)
    def get_token(self, response):
        token = re.search('instance_token=(.+?);',
                          response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, scene):
        image_arr = []
        if 'card_main_rect' in scene['images'] and len(
                scene['images']['card_main_rect']):
            image_arr = scene['images']['card_main_rect']
        elif 'poster' in scene['images'] and len(scene['images']['poster']):
            image_arr = scene['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']

    def get_trailer(self, scene):
        for index in scene['videos']:
            trailer = scene['videos'][index]
            for size in ['720p', '576p', '480p', '360p', '320p', '1080p', '4k']:
                if size in trailer['files']:
                    return trailer['files'][size]['urls']['view']

    def clean_markers(self, markers):
        markers = sorted(markers, key=lambda k: (k['name'].lower(), int(k['start']), int(k['end'])))
        marker_final = []
        marker_work = markers.copy()
        marker2_work = markers.copy()
        for test_marker in marker_work:
            if test_marker in markers:
                for marker in marker2_work:
                    if test_marker['name'].lower().strip() == marker['name'].lower().strip():
                        test_start = int(test_marker['start'])
                        mark_start = int(marker['start'])
                        test_end = int(test_marker['end'])
                        mark_end = int(marker['end'])
                        if test_start < mark_start or test_start == mark_start:
                            test1 = mark_start - test_end
                            test2 = mark_start - test_start
                            if 0 < test1 < 60 or 0 < test2 < 60 or test1 == 0 or test2 == 0:
                                if mark_end > test_end:
                                    test_marker['end'] = marker['end']
                                    if marker in markers:
                                        markers.remove(marker)
                            if test_end > mark_start and mark_end > test_end:
                                test_marker['end'] = marker['end']
                                if marker in markers:
                                    markers.remove(marker)
                            if test_start < mark_start and (mark_end < test_end or test_end == mark_end):
                                if marker in markers:
                                    markers.remove(marker)
                marker2_work = markers.copy()

                if test_marker in markers:
                    marker_final.append(test_marker)
                    markers.remove(test_marker)
        marker_final = sorted(marker_final, key=lambda k: (int(k['start']), int(k['end'])))
        return marker_final
