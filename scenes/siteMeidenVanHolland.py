import re
from datetime import date, timedelta
import codecs
import string
import json
import scrapy
from tpdb.items import SceneItem

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_tag(argument):
    match = {
        'debutanten': "First Time",
        'anaal': "Anal",
        'blondje': "blonde",
        'dikke tieten': "Big Boobs",
        'amateur sex': "Amateur",
        'volle vrouw': "BBW",
        'duo': "FM",
        'neuken: 1 op 1': "1on1",
        'gangbang': "Gangbang",
        'trio': "Threesome",
        'jonge meid': "18+ Teens",
        'squirten': "Squirting",
        'pov': "POV",
        'lesbisch': "Lesbian",
        'lesbische sex': "Lesbian",
        'pijpen': "Blowjob",
        'buitensex': "Outdoors",
        'bdsm': "BDSM",
        'rollenspel': "Roleplay",
        'tattoo meid': "Tattoos",
        'vlaams': "Flemish",
        'trio: 2 meiden & 1 man': "FFM",
        'romantische sex': "Romantic",
        'internationaal': "International",
        'interraciaal': "Interracial",
        'klassiekers': "Classics",
        'milf': "MILF",
        'gilf': "GILF",
    }
    return match.get(argument.lower(), argument)


class SiteMedienVanHolldandSpider(BaseSceneScraper):
    name = 'MeidenVanHolland'
    network = 'Meiden Van Holland'
    parent = 'Meiden Van Holland'
    site = 'Meiden Van Holland'

    base_url = 'https://meidenvanholland.nl'

    headers_json = {
        'accept': 'application/json, text/plain, */*',
        'credentials': 'sysero 1-3dc13a570ff233c78a3fef0b887ad44f279683fe036ccbac8e494bb89422ed77-mvh',
        'origin': 'https://meidenvanholland.nl',
        'referer': 'https://meidenvanholland.nl',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'MEDIA_ALLOW_REDIRECTS': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'RETRY_ENABLED': True,
        'HANDLE_HTTPSTATUS_LIST': [307,404,403],
    }

    selector_map = {
        'title': '//script[contains(text(),"NUXT")]/text()',
        're_title': r'video:\{title:\"(.*?)\"',
        'description': '//script[contains(text(),"NUXT")]/text()',
        're_description': r'description:\"(.*?)\"',
        'date': '//script[contains(text(),"NUXT")]/text()',
        're_date': r'pivot_data:\{active_from:\"(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "video trailer")]/div[@class="thumb videoratio"]/img/@data-src',
        'performers': '//script[contains(text(),"NUXT")]/text()',
        're_performers': r'models:\[(.*?)\]',
        'tags': '//script[contains(text(),"NUXT")]/text()',
        'external_id': r'sexfilms\/(.*)',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_next_page_url(self, base, page):
        url = 'https://apiv2.sysero.nl/api/mvh/resources/nl?query=(content%3Avideos%2Ctypes%3A(0%3Avideo)%2Csort%3A(published_at%3ADESC)%2Cfilters%3A(status%3Apublished)%2Cpagination%3A(page%3A{}%2Cper_page%3A20)%2Cinclude%3A((resources%3A(filters%3A((types%3A(0%3Acategory)%2Cstatus%3Apublished))%2Cimages%3A(filters%3A((types%3A(0%3Athumb)))))%2Cimages%3A(filters%3A((types%3A(0%3Acover%2C1%3Ahome_cover%2C2%3Athumb%2C3%3Acover_thumb))))%2Cclips%3A()%2Cvideos%3A()%2Ccategories%3A())))'
        return self.format_url(base, url.format(page))

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = 'https://meidenvanholland.nl/sexfilms'
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers_json, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        yield scrapy.Request(url=self.get_next_page_url(self.base_url, self.page), callback=self.parse, meta=meta, headers=self.headers_json)

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
                yield scrapy.Request(url=self.get_next_page_url(
                                     response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers_json,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            if jsonentry['slug']:
                meta['scene_url'] = "https://meidenvanholland.nl/sexfilms/" + jsonentry['slug']
                link = 'https://apiv2.sysero.nl/api/mvh/resource/{}/nl?query=(content%3Avideo%2Ctypes%3A(0%3Avideo)%2Csort%3A(recommended_at%3Adesc)%2Cfilters%3A(status%3Apublished)%2Cinclude%3A((resources%3A(filters%3A((types%3A(0%3Acategory%2C1%3Afilm_collection%2C2%3Amodel)%2Cstatus%3Apublished))%2Cinclude%3A((resources%3A(filters%3A((types%3A(0%3Avideo)%2Cstatus%3Apublished))%2Cinclude%3A((images%3A(filters%3A((types%3A(0%3Acover%2C1%3Ahome_cover%2C2%3Athumb%2C3%3Acover_thumb)))))))%2Cimages%3A(filters%3A((types%3A(0%3Acover%2C1%3Ahome_cover%2C2%3Athumb%2C3%3Acover_thumb)))))))%2Cimages%3A()%2Crelated%3A(filters%3A((types%3A(0%3Avideo)%2Cstatus%3Apublished))%2Cinclude%3A((images%3A(filters%3A((types%3A(0%3Acover%2C1%3Athumb)))))))%2Cseo%3A()%2Cclips%3A()%2Cvideos%3A()%2Ccategories%3A()%2Cmodels%3A())))'
                link = link.format(jsonentry['slug'])
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta, headers=self.headers_json)

    def parse_scene(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        scene = jsondata['data']
        item = self.init_scene()
        item['id'] = scene['id']
        item['title'] = string.capwords(scene['title'])
        item['description'] = re.sub('<[^<]+?>', '', scene['description'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['active_from']).group(1)
        item['image'] = f"https://cdndo.sysero.nl{scene['images']['data']['thumb'][0]['path']}"
        item['url'] = meta['scene_url']
        item['performers'] = []
        for resource in scene['resources']['data']:
            if resource['type'] == "model":
                item['performers'].append(resource['title'])
        item['tags'] = []
        for resource in scene['resources']['data']:
            if resource['type'] == "category":
                item['tags'].append(match_tag(resource['title']))
        try:
            item['duration'] = scene['videos']['data']['film'][0]['duration']
        except:
            item['duration'] = None
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        if item['date'] > '2025-02-18':
            yield self.check_item(item, self.days)



