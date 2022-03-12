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

link_to_info = {
    "SLM-organic-b75inmn9fu": {
        "site": "Sis Loves Me",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "FS-organic-1rstmyhj44": {
        "site": "Family Strokes",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "ts-elastic-d5cat0jl5o": {
        "site": "Team Skeet",
        "navText": v2_videos_content_text,
        "contentText": v2_videos_content_text,
        "v2": True
    },
    "mylf-elastic-hka5k7vyuw": {
        "site": "MYLF",
        "navText": v2_videos_content_text,
        "contentText": v2_videos_content_text,
        "v2": True
    },
    "FOS-organic-n5oaginage": {
        "site": "Foster Tapes",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "DSW-organic-dfangeym88": {
        "site": "Daughter Swap",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "DC-organic-w8xs8e0dv3": {
        "site": "Dad Crush",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "MSL-organic-ws9h564all": {
        "site": "ShopLyfter MYLF",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "SHL-organic-driobt7t0f": {
        "site": "ShopLyfter",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "PVM-organic-rg7wwuc7uh": {
        "site": "PervMom",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "TMZ-organic-958spxinbs": {
        "site": "Thickumz",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "LAS-organic-whlghevsfs": {
        "site": "Little Asians",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "BFFS-organic-7o68xoev0j": {
        "site": "BFFs",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "TLBC-organic-w8bw4yp9io": {
        "site": "Teens Love Black Cocks",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "BCG-organic-dhed18vuav": {
        "site": "Black Valley Girls",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-fuf-eiBei5In": {
        "site": "Freeuse Fantasy",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "Organic-pna-OongoaF1": {
        "site": "Perv Nana",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-Baepha2v-1": {
        "site": "Not My Grandpa",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-mylfdom-ieH7cuos%20": {
        "site": "MYLFDom",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-1-goide6Xo": {
        "site": "BBC Paradise",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-alm-Od3Iqu9I": {
        "site": "Anal Mom",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-Freeusemilf-uug2tohT": {
        "site": "Free Use MILF",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-momswap-6fkccwxhi0": {
        "site": "Mom Swap",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-hhk-am7zoi2G": {
        "site": "Hijab Hookups",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-doc-utei5Mai": {
        "site": "Perv Doctor",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-shm-iev4iCh6": {
        "site": "Stay Home MILF",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-sss-no7OhCoo": {
        "site": "Step Siblings",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-pvt-fePaiz9a": {
        "site": "Perv Therapy",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-swp-Jo4daep7": {
        "site": "Sis Swap",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    "organic-1-saeXae9v": {
        "site": "Tiny Sis",
        "navText": movies_nav_text,
        "contentText": movies_content_text,
        "v2": False
    },
    # ~ "Organic-bad-aiGhaiL5": {
    # ~ "site": "BadMILFs",
    # ~ "navText": movies_nav_text,
    # ~ "contentText": movies_content_text,
    # ~ "v2": False
    # ~ },
}


def format_nav_url(link, start, limit, v2=False):
    if v2:
        nav_format = "https://store2.psmcdn.net/{link}-{navText}/_search?from={start}&size={limit}"
    else:
        nav_format = "https://store.psmcdn.net/{link}/{navText}/items.json?orderBy=\"$key\"&startAt=\"{start}\"&limitToFirst={limit}"

    return nav_format.format(link=link, start=start, limit=limit, navText=link_to_info[link]["navText"])


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


class TeamSkeetNetworkSpider(BaseSceneScraper):
    name = 'TeamSkeetNetwork'
    network = 'teamskeet'

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
                limit = 250
            else:
                start = "aaaaaaaa"
                limit = 450
            yield scrapy.Request(url=format_nav_url(linkName, start, limit, is_v2),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': siteInfo['site'], 'is_v2': is_v2},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        highwater = ""
        if not meta['is_v2']:
            scene_list = json.loads(response.body)
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
        data = response.json()
        item = SceneItem()
        is_v2 = "store2" in response.url

        if "store2" in response.url:
            data = data['_source']
        item['title'] = data['title']
        item['description'] = data['description']
        item['image'] = data['img']
        item['image_blob'] = None
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
            item['date'] = self.parse_date(data['publishedDate']).isoformat()
        else:
            item['date'] = self.parse_date('today').isoformat()

        if 'site' in data:
            if 'name' in data['site']:
                item['site'] = data['site']['name']
            else:
                item['site'] = response.meta['site']
        else:
            item['site'] = response.meta['site']

        if is_v2:
            item['url'] = "https://www.teamskeet.com/movies/" + data['id']
        else:
            item['url'] = "https://www." + response.meta['site'].replace(" ", "").lower() + ".com/movies/" + data['id']

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
                if item['date'] > filterdate:
                    yield item
            else:
                yield item

    def get_scenes(self, response):
        scene_info = json.loads(response.body)
        is_v2 = "store2" in response.url
        site_link = get_site_link_text(response.url, is_v2)

        if is_v2:
            for scene in scene_info['hits']['hits']:
                scene = scene['_source']
                if "id" in scene:
                    scene_id = scene["id"]
                    scene_url = format_scene_url(site_link, scene_id, is_v2)
                    yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=response.meta)
        else:
            if scene_info:
                for key, scene in scene_info.items():
                    if "id" in scene:
                        scene_id = scene["id"]
                        scene_url = format_scene_url(site_link, scene_id, is_v2)
                        yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=response.meta)

    def get_next_page_url(self, base, page, highwater):
        limit = 250
        if 'store2' in base:
            start = str(250 * (page - 1))
            is_v2 = True
        else:
            is_v2 = False
            if highwater:
                start = highwater
            else:
                start = 'aaaaabka'
        linkName = get_site_link_text(base, is_v2)
        return format_nav_url(linkName, start, limit, is_v2)
