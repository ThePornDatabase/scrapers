import re
import html
import json
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkItsPOVSpider(BaseSceneScraper):
    name = 'ItsPOV'
    network = 'Its POV'

    url = 'https://itspov.com/'

    sites = [
        ['OfficePOV', '77'],
        ['BackdoorPOV', '74'],
        ['IntimatePOV', '76'],
        ['FeetishPOV', '75'],
        ['SchoolPOV', '78'],
        ['StepPOV', '102'],
        ['PetitePOV', '107'],
    ]

    headers = {
        'Siteid': '102',
        'Token': 'mysexmobile',
    }

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',

                       'ITEM_PIPELINES': {
                           'tpdb.pipelines.TpdbApiScenePipeline': 400,
                       },
                       'DOWNLOADER_MIDDLEWARES': {
                           'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
                       }
                       }

    selector_map = {
        'image': '//div[@class="tour-video-title"]/following-sibling::a/img/@style',
        're_image': r'\((.*\.jpg)\)',
        'tags': '//a[contains(@class,"btn-outline-secondary")]/text()',
        'performers': '//a[contains(@class,"btn-secondary")]/text()',
        'external_id': '',
        'pagination': ''
    }

    def start_requests(self):
        yield scrapy.Request("https://itspov.com/en/",
                             callback=self.start_requests2,
                             headers=self.headers,
                             cookies=self.cookies)

    def start_requests2(self, response):
        for site in self.sites:
            url = "https://content-api.itspov.com/24api/v1/sites/{}/freetour".format(site[1])
            yield scrapy.Request(url,
                                 callback=self.get_scenes,
                                 meta={'page': self.page, 'site': site[0], 'group': site[1]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsonslice = jsondata['payload']['sites'][meta['group']]['scenes']

        # set up pseudo-paging
        counter = 0
        if not self.limit_pages:
            limit_pages = 1
        elif self.limit_pages == "all" or not int(self.limit_pages):
            limit_pages = 999
        else:
            limit_pages = int(self.limit_pages)

        for data in jsonslice:
            counter += 1
            if counter > (limit_pages * 5):
                break

            url = "https://content-api.itspov.com/24api/v1/sites/{}/freetour/videos/".format(meta['group']) + str(jsondata['payload']['sites'][meta['group']]['scenes'][data]['id'])
            yield scrapy.Request(url,
                                 callback=self.parse_scene,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        # The site uses a rate limit of 40 requests in a given minute.
        if 'X-Ratelimit-Remaining' in response.headers:
            ratelimit = int(response.headers['X-Ratelimit-Remaining'])
        try:
            jsondata = json.loads(response.text)
        except:
            print(f'Failed retrieving {response.url}.  X-Ratelimit was: {ratelimit}')

        data = jsondata['payload']['scenes']
        for row in data:
            item = SceneItem()
            item['id'] = data[row]['id']
            item['title'] = html.unescape(re.sub('<[^<]+?>', '', data[row]['title']))
            item['description'] = html.unescape(re.sub('<[^<]+?>', '', data[row]['story']))
            item['url'] = "https://itspov.com/" + data[row]['url']
            item['image'] = data[row]['video_cover']['1500']
            item['image_blob'] = None
            item['date'] = self.parse_date(data[row]['translations'][0]['created_at']).isoformat()
            item['performers'] = []
            for model in data[row]['models']:
                item['performers'].append(data[row]['models'][model]['stage_name'])
            item['tags'] = []
            for tag in data[row]['main_scenetags']:
                item['tags'].append(data[row]['main_scenetags'][tag]['name'].strip().title())

            item['trailer'] = ''
            item['site'] = meta['site']
            item['parent'] = meta['site']
            item['network'] = 'Its POV'

            if item['id'] and item['title']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item
