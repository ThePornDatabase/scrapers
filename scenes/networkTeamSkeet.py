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
    "ts-organic-iiiokv9kyo": {
        "site": "Team Skeet",
        "navText": videos_nav_text,
        "contentText": videos_content_text
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


def format_nav_url(link, start, limit):
    nav_format = "https://store.psmcdn.net/{link}/{navText}/items.json?orderBy=\"$key\"&startAt=\"{start}\"&limitToFirst={limit}"
    return nav_format.format(link=link, start=start,
                             limit=limit, navText=link_to_info[link]["navText"])


def format_scene_url(link, sceneId):
    content_format = "https://store.psmcdn.net/{link}/{contentText}/{sceneId}.json"
    return content_format.format(
        link=link, sceneId=sceneId, contentText=link_to_info[link]["contentText"])


def get_site_link_text(url):
    pattern = r"store.psmcdn.net\/([^\/]+)\/"
    site_link = re.search(pattern, url).groups()[0]
    return site_link


class TeamSkeetNetworkSpider(BaseSceneScraper):
    name = 'TeamSkeetNetwork'
    network = 'teamskeet'
    parent = 'teamskeet'

    selector_map = {
        'external_id': '\\/(.+)\\.json'
    }

    def start_requests(self):
        start = "aaaaaaaa"
        limit = 250
        for linkName, siteInfo in link_to_info.items():
            meta = {'site': siteInfo['site']}
            yield scrapy.Request(url=format_nav_url(linkName, start, limit), callback=self.get_scenes, meta=meta)

    def parse_scene(self, response):
        data = response.json()
        item = SceneItem()
        item['title'] = data['title']
        item['description'] = data['description']
        item['image'] = data['img']
        item['tags'] = []
        item['id'] = data['id']
        item['trailer'] = 'https://videodelivery.net/' + \
                          data['video'] + '/manifest/video.m3u8'
        item['url'] = response.url
        item['network'] = self.network
        item['parent'] = self.parent

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

        item['performers'] = []
        for model in data['models']:
            item['performers'].append(model['modelName'])

        if self.debug:
            print(item)
        else:
            yield item

    def get_scenes(self, response):
        scene_info = json.loads(response.body)
        site_link = get_site_link_text(response.url)

        for key, scene in scene_info.items():
            if "id" in scene:
                scene_id = scene["id"]
                scene_url = format_scene_url(site_link, scene_id)
                yield scrapy.Request(url=scene_url, callback=self.parse_scene, meta=response.meta)
