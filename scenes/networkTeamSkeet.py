import json
import re
from datetime import datetime

import dateparser
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
        "contentText": movies_content_text
    },
    "FS-organic-1rstmyhj44": {
        "site": "Family Strokes",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "ts-elastic-d5cat0jl5o": {
        "site": "Team Skeet",
        "navText": v2_videos_content_text,
        "contentText": v2_videos_content_text,
        "v2": True
    },
    "mylf-organic-2uxkybtwvv": {
        "site": "MYLF",
        "navText": videos_nav_text,
        "contentText": videos_content_text
    },
    "FOS-organic-n5oaginage": {
        "site": "Foster Tapes",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "DSW-organic-dfangeym88": {
        "site": "Daughter Swap",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "DC-organic-w8xs8e0dv3": {
        "site": "Dad Crush",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "MSL-organic-ws9h564all": {
        "site": "ShopLyfter MYLF",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "SHL-organic-driobt7t0f": {
        "site": "ShopLyfter",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "PVM-organic-rg7wwuc7uh": {
        "site": "PervMom",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "TMZ-organic-958spxinbs": {
        "site": "Thickumz",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "LAS-organic-whlghevsfs": {
        "site": "Little Asians",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "BFFS-organic-7o68xoev0j": {
        "site": "BFFs",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "TLBC-organic-w8bw4yp9io": {
        "site": "Teens Love Black Cocks",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "BCG-organic-dhed18vuav": {
        "site": "Black Valley Girls",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "organic-fuf-eiBei5In": {
        "site": "Freeuse Fantasy",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "Organic-pna-OongoaF1": {
        "site": "PervNana",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "organic-Baepha2v-1": {
        "site": "Not My Grandpa",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "organic-mylfdom-ieH7cuos": {
        "site": "MYLFDom",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "organic-1-goide6Xo": {
        "site": "BBC Paradise",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    },
    "organic-alm-Od3Iqu9I": {
        "site": "Anal Mom",
        "navText": movies_nav_text,
        "contentText": movies_content_text
    }
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
        limit = 250

        for linkName, siteInfo in link_to_info.items():
            if 'v2' in siteInfo:
                is_v2 = siteInfo['v2']
            else:
                is_v2 = False
            if is_v2:
                start = "0"
            else:
                start = "aaaaaaaa"
            url=format_nav_url(linkName, start, limit, is_v2)
            yield scrapy.Request(url=format_nav_url(linkName, start, limit, is_v2),
                                 callback=self.parse,
                                 meta={'page': self.page, 'site': siteInfo['site']},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        limit = 250
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
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
            item['date'] = dateparser.parse(data['publishedDate']).isoformat()
        else:
            item['date'] = datetime.now().isoformat()

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

        if self.debug:
            print(item)
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


    def get_next_page_url(self, base, page):
        limit = 250
        if 'store2' in base:
            start = str(250 * (page-1))
            is_v2 = True
        else:
            is_v2 = False
            start = 'aaaaabka'
        linkName = get_site_link_text(base, is_v2)
        return format_nav_url(linkName, start, limit, is_v2)
