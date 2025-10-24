import json
import re
import scrapy
import urllib.parse
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
    "mylf-reg": {"urlid": "mylf-elastic-hka5k7vyuw", "site": "MYLF", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": False},
    "ts-reg": {"urlid": "ts-elastic-d5cat0jl5o", "site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": False},
    "su-reg": {"urlid": "sau-elastic-00gy5fg5ra", "site": "Say Uncle", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": False},
    "mylf-xsite": {"urlid": "mylf-elastic-hka5k7vyuw", "site": "MYLF", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": True},
    "ts-xsite": {"urlid": "ts-elastic-d5cat0jl5o", "site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": True},
    "familybundle": {"urlid": "ts-elastic-d5cat0jl5o", "site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": "Bundle"},
    "freeusebundle": {"urlid": "ts-elastic-d5cat0jl5o", "site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": "Bundle"},
    "swap_bundle": {"urlid": "ts-elastic-d5cat0jl5o", "site": "Team Skeet", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": "Bundle"},
    "mylf_ppv": {"urlid": "ts-elastic-d5cat0jl5o", "site": "MYLF", "navText": v2_videos_content_text, "contentText": v2_videos_content_text, "v2": True, "xsite": "Bundle"},
}

def format_nav_url(link, start, limit, sitekey, v2=False, xsite=False):
    if xsite is True:
        nav_format = "https://tours-store.psmcdn.net/{link}-{navText}/_search?sort=publishedDate:desc&q=(isUpcoming:false%20AND%20isXSeries:%20true)&size={limit}&from={start}"
        nav_url = nav_format.format(link=link, start=start, limit=limit, navText=link_to_info[sitekey]["navText"])
    elif xsite == "Bundle":
        nav_url = f"https://tours-store.psmcdn.net/{sitekey}/_search?sort=publishedDate:desc&q=(type:video%20)&size={limit}&from={start}"
        # ~ print(nav_url)
    else:
        nav_format = "https://tours-store.psmcdn.net/{link}-{navText}/_search?sort=publishedDate:desc&q=(isUpcoming:false%20AND%20isXSeries:%20false)&size={limit}&from={start}"
        nav_url = nav_format.format(link=link, start=start, limit=limit, navText=link_to_info[sitekey]["navText"])

    return nav_url


def format_scene_url(link, sceneId, sitekey, v2=False, xsite=False):
    if xsite != "Bundle":
        content_format = "https://tours-store.psmcdn.net/{link}-{contentText}/_doc/{sceneId}"
        return content_format.format(link=link, sceneId=sceneId, contentText=link_to_info[sitekey]["contentText"])
    else:
        content_format = f"https://tours-store.psmcdn.net/{sitekey}/_search?q=(id:{sceneId}%20AND%20type:video)&size=1"
        # ~ print("Scene URL: " + content_format)
        return content_format


def get_site_link_text(url, v2=False):
    pattern = r"tours-store.psmcdn.net\/([^\/]+)-.*\/"
    site_link = re.search(pattern, url)
    if not site_link:
        pattern = r"tours-store.psmcdn.net/(.*?)/"
        site_link = re.search(pattern, url)
    site_link = site_link.groups()[0]

    return site_link


class TeamSkeetNetworkPlaywrightSpider(BaseSceneScraper):
    name = 'TeamSkeetNetworkPlaywright'
    network = 'teamskeet'

    # ~ custom_scraper_settings = {
        # ~ 'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        # ~ 'AUTOTHROTTLE_START_DELAY': 1,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 60,
        # ~ 'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 2,
        # ~ 'DOWNLOADER_MIDDLEWARES': {
            #'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            # ~ 'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            # ~ 'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            # ~ 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            # ~ 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # ~ 'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            # ~ 'scrapy_fake_useragent.middleware.RetryUserAgentMiddleware': 401,
        # ~ },
        # ~ 'DOWNLOAD_HANDLERS': {
            # ~ "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            # ~ "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        # ~ }
    # ~ }

    selector_map = {
        'external_id': '\\/(.+)\\.json'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for linkName, siteInfo in link_to_info.items():
            # ~ print(linkName, siteInfo)
            if 'v2' in siteInfo:
                is_v2 = siteInfo['v2']
            else:
                is_v2 = False
            if is_v2:
                start = str((int(meta['page']) - 1) * 30)
                limit = "30"
            url = format_nav_url(siteInfo['urlid'], start, limit, linkName, is_v2, siteInfo['xsite'])
            print(f"Page 1 URL: {url}")
            meta['sitekey'] = linkName
            meta['xsite'] = siteInfo['xsite']
            yield scrapy.Request(url, callback=self.parse, meta={'page': meta['page'], 'site': siteInfo['site'], 'xsite': siteInfo['xsite'], 'is_v2': is_v2, "playwright": False, 'sitekey': linkName}, headers=self.headers, cookies=self.cookies, dont_filter=True)
            # ~ yield scrapy.Request(url, callback=self.parse, meta={'page': meta['page'], 'site': siteInfo['site'], 'xsite': siteInfo['xsite'], 'is_v2': is_v2}, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        # ~ print(f"Back in Parse for Page {meta['page']}")
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        # ~ print(meta['page'], self.limit_pages)
        if count:
            if 'page' in meta and meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                url = self.get_next_page_url(response.url, meta['page'], meta['xsite'], meta['sitekey'])
                print(f"Next Page #{meta['page']} URL: {url}")
                yield scrapy.Request(url, callback=self.parse, meta=meta, dont_filter=True)

    def parse_scene(self, response):
        meta = response.meta
        body = re.search(r'({.*})', response.text)
        if body:
            body = body.group(1)
            data = json.loads(body)
        else:
            data = ''
        item = SceneItem()
        # ~ print(data)
        if ('isUpcoming' in data and not data['isUpcoming']) or 'isUpcoming' not in data:
            is_v2 = "tours-store" in response.url

            if meta['xsite'] != "Bundle":
                data = data['_source']
            else:
                data = data['hits']['hits'][0]['_source']
            item['title'] = data['title']
            item['description'] = data['description']

            if 'publishedDate' in data:
                item['date'] = self.parse_date(data['publishedDate']).strftime('%Y-%m-%d')
            else:
                item['date'] = None

            if self.check_item(item, self.days):
                item['image'] = data['img']
                if "med.jpg" in item['image']:
                    item['image'] = item['image'].replace("med.jpg", "hi.jpg")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                if 'tags' in data:
                    item['tags'] = data['tags']
                else:
                    item['tags'] = []
                # ~ print(item['tags'])
                # ~ print()
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

                if 'site' in data:
                    if 'name' in data['site']:
                        item['site'] = data['site']['name']
                    else:
                        item['site'] = response.meta['site']
                else:
                    item['site'] = response.meta['site']

                if is_v2:
                    if "Say Uncle" in response.meta['site']:
                        item['url'] = "https://www.sayuncle.com/movies/" + urllib.parse.quote_plus(data['id'])
                    elif "MYLF" in response.meta['site']:
                        item['url'] = "https://www.mylf.com/movies/" + urllib.parse.quote_plus(data['id'])
                    else:
                        item['url'] = "https://www.teamskeet.com/movies/" + urllib.parse.quote_plus(data['id'])

                else:
                    item['url'] = "https://www." + response.meta['site'].replace(" ", "").lower() + ".com/movies/" + urllib.parse.quote_plus(data['id'])
                item['url'] = item['url'].replace("hijabhookups", "hijabhookup")
                item['url'] = item['url'].replace("-–", "-")
                # ~ print(item['url'])

                item['performers'] = []
                if 'models' in data:
                    item['performers_data'] = []
                    for model in data['models']:
                        if "modelName" in model:
                            performer = model['modelName']
                        elif "name" in model:
                            performer = model['name']
                        performer_extra = {}
                        performer_extra['site'] = "Team Skeet"
                        performer_extra['name'] = performer
                        performer_extra['extra'] = {}
                        if "gender" in model and model['gender']:
                            performer_extra['extra']['gender'] = model['gender'].title()
                        if "ethnicity" in model and model['ethnicity']:
                            performer_extra['extra']['ethnicity'] = model['ethnicity']
                        if "hairColor" in model and model['hairColor']:
                            performer_extra['extra']['haircolor'] = model['hairColor']
                        if "img" in model and model['img']:
                            perf_image = model['img']
                            if perf_image:
                                perf_image = perf_image
                                performer_extra['image'] = perf_image
                                performer_extra['image_blob'] = self.get_image_blob_from_link(performer_extra['image'])
                                if not performer_extra['image_blob']:
                                    performer_extra['image_blob'] = ""
                                    performer_extra['image'] = ""
                        item['performers'].append(performer)
                        if performer_extra['extra']:
                            item['performers_data'].append(performer_extra)
                if "performers_data" in item and not item['performers_data']:
                    del item['performers_data']

                yield self.check_item(item, self.days)

    def get_scenes(self, response):
        meta = response.meta
        body = re.search(r'({.*})', response.text)
        if body:
            body = body.group(1)
            scene_info = json.loads(body)
            if 'hits' not in scene_info or 'hits' not in scene_info['hits'] or not len(scene_info['hits']['hits']):
                print(f"Retrying index page {response.url}")
                yield scrapy.Request(response.url, callback=self.parse, meta=meta, dont_filter=True)

            is_v2 = "tours-store" in response.url
            site_link = get_site_link_text(response.url, is_v2)
            meta['body'] = body

            for scene in scene_info['hits']['hits']:
                scene = scene['_source']
                # ~ print(scene)
                if "id" in scene:
                    scene_id = scene["id"]
                    scene_url = format_scene_url(site_link, scene_id, meta['sitekey'], is_v2, meta['xsite'])
                    # ~ print("Scene URL: " + scene_url)
                    yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page, xsite, sitekey):
        limit = "30"
        start = str(int(limit) * (page - 1))
        is_v2 = True
        linkName = get_site_link_text(base, is_v2)
        return format_nav_url(linkName, start, limit, sitekey, is_v2, xsite)
