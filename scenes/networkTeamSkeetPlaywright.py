import json
import re
from datetime import date, timedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

movies_nav_text = "newestMovies"
videos_nav_text = "latestVideos"
movies_content_text = "moviesContent"
videos_content_text = "videosContent"
v2_videos_content_text = "videoscontent"
false = False
true = True

link_to_info = {
    "mylf-elastic-hka5k7vyuw": {"site": "MYLF", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True},
    "ts-elastic-d5cat0jl5o": {"site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True},
    "sau-elastic-00gy5fg5ra": {"site": "Say Uncle", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True},
}


def format_nav_url(link, start, limit, v2=False):
    if v2:
        nav_format = "https://store2.psmcdn.net/{link}-{navText}/_search?sort=publishedDate:desc&q=isUpcoming:false&from={start}&size={limit}"
    else:
        nav_format = "https://store.psmcdn.net/{link}/{navText}/items.json?orderBy=\"$key\"&startAt=\"{start}\"&limitToFirst={limit}"

    nav_url = nav_format.format(link=link, start=start, limit=limit, navText=link_to_info[link]["navText"])

    return nav_url


def format_scene_url(link, sceneId, v2=False):
    if v2:
        content_format = "https://store2.psmcdn.net/{link}-{contentText}/_doc/{sceneId}"
    else:
        content_format = "https://store.psmcdn.net/{link}/{contentText}/{sceneId}.json"

    return content_format.format(link=link, sceneId=sceneId, contentText=link_to_info[link]["contentText"])


def get_site_link_text(url, v2=False):
    if v2:
        pattern = r"store2.psmcdn.net\/([^\/]+)-.*\/"
    else:
        pattern = r"store.psmcdn.net\/([^\/]+)\/"

    site_link = re.search(pattern, url).groups()[0]

    return site_link


class TeamSkeetNetworkPlaywrightSpider(BaseSceneScraper):
    name = 'TeamSkeetNetworkPlaywright'
    network = 'teamskeet'

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # ~ 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    selector_map = {
        'external_id': '\\/(.+)\\.json'
    }

    def start_requests(self):

        for linkName, siteInfo in link_to_info.items():
            if 'v2' in siteInfo:
                is_v2 = siteInfo['v2']
            else:
                is_v2 = False
            if is_v2:
                start = "0"
                limit = 150
            else:
                start = "aaaaaaaa"
                limit = 150  # Was originally 450.  Next Page is keyed at 450
            yield scrapy.Request(url=format_nav_url(linkName, start, limit, is_v2),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': siteInfo['site'], 'is_v2': is_v2, "playwright": True},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        highwater = ""
        if not meta['is_v2']:
            scene_list = re.search(r'({.*})', response.text)
            if scene_list:
                scene_list = scene_list.group(1)
                scene_list = json.loads(scene_list)
            if scene_list:
                for key, scene in scene_list.items():
                    if key > highwater:
                        highwater = key
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], highwater),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def parse_scene(self, response):
        body = re.search(r'({.*})', response.text)
        if body:
            body = body.group(1)
            data = json.loads(body)
        else:
            data = ''
        item = SceneItem()
        if ('isUpcoming' in data and not data['isUpcoming']) or 'isUpcoming' not in data:
            is_v2 = "store2" in response.url

            if "store2" in response.url:
                data = data['_source']
            item['title'] = data['title']
            item['description'] = data['description']
            item['image'] = data['img']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if 'tags' in data:
                item['tags'] = data['tags']
            else:
                item['tags'] = []
            item['id'] = data['id']

            if 'videoTrailer' in data:
                item['trailer'] = data['videoTrailer']
            elif 'video' in data:
                item['trailer'] = 'https://videodelivery.net/' + \
                                  data['video'] + '/manifest/video.m3u8'
            else:
                item['trailer'] = ''

            item['network'] = self.network
            item['parent'] = response.meta['site']

            if 'publishedDate' in data:
                item['date'] = self.parse_date(data['publishedDate']).strftime('%Y-%m-%d')
            else:
                item['date'] = None

            if 'site' in data:
                if 'name' in data['site']:
                    item['site'] = data['site']['name']
                else:
                    item['site'] = response.meta['site']
            else:
                item['site'] = response.meta['site']

            if is_v2:
                if "Say Uncle" in response.meta['site']:
                    item['url'] = "https://www.sayuncle.com/movies/" + data['id']
                else:
                    item['url'] = "https://www.teamskeet.com/movies/" + data['id']

            else:
                item['url'] = "https://www." + response.meta['site'].replace(" ", "").lower() + ".com/movies/" + data['id']
            item['url'] = item['url'].replace("hijabhookups", "hijabhookup")
            item['url'] = item['url'].replace("-–", "-")
            # ~ print(item['url'])

            item['performers'] = []
            if 'models' in data:
                for model in data['models']:
                    item['performers'].append(model['modelName'])

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
                    if (item['date'] and item['date'] > filterdate) or not item['date']:
                        yield item
                else:
                    yield item

    def get_scenes(self, response):
        body = re.search(r'({.*})', response.text)
        if body:
            body = body.group(1)
            scene_info = json.loads(body)
            is_v2 = "store2" in response.url
            site_link = get_site_link_text(response.url, is_v2)
            meta = response.meta
            meta['body'] = body

            if is_v2:
                for scene in scene_info['hits']['hits']:
                    scene = scene['_source']
                    if "id" in scene:
                        scene_id = scene["id"]
                        scene_url = format_scene_url(site_link, scene_id, is_v2)
                        yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=meta)
            else:
                if scene_info:
                    for key, scene in scene_info.items():
                        if "id" in scene:
                            scene_id = scene["id"]
                            scene_url = format_scene_url(site_link, scene_id, is_v2)
                            yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page, highwater):
        limit = 25
        if 'store2' in base:
            start = str(25 * (page - 1))
            is_v2 = True
        else:
            is_v2 = False
            if highwater:
                start = highwater
            else:
                start = 'aaaaabka'
        linkName = get_site_link_text(base, is_v2)
        return format_nav_url(linkName, start, limit, is_v2)
