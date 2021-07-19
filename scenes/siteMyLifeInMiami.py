import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
import re
import dateparser
import json
import html
import string

from datetime import datetime
from tpdb.items import SceneItem

class siteMyLifeInMiamiSpider(BaseSceneScraper):
    name = 'MyLifeInMiami'
    network = "My Life In Miami"
    parent = "My Life In Miami"

    start_urls = [
        'https://www.mylifeinmiami.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': 'scene\/(\d+)\/',
        'pagination': '/home_page=%s'
    }
    
    headers = {
        'splash': '1',
        '__ax': 'cdcSh4XJ3QtT2o75dGTCW',
    }
    
    def start_requests(self):
        for link in self.start_urls:
            url = url=self.get_next_page_url(link, self.page)
            yield scrapy.Request(url,
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page):
        page = str((int(page)-1) * 10)
        page_url = "https://mylifeinmiami.com/sapi/GYyADCCqcoe2R9z0Cge7dw/1626714741/event.last?_method=event.last&offset=%s&limit=10&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[showOnHome]=true"
        return self.format_url(base, page_url % page)


    def get_scenes(self, response):
        global json
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']
        
        for scene in jsondata:
            scene_id = scene['_typedParams']['id']
            scene_url = "https://mylifeinmiami.com/sapi/Qld8qiCJ5S9rIJLaJkBnFw/1626716371/content.load?_method=content.load&tz=-4&filter[id][fields][0]=id&filter[id][values][0]=%s&limit=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[preset]=scene" % scene_id
            yield scrapy.Request(scene_url, callback=self.parse_scene)


    def parse_scene(self, response):
        item = SceneItem()
        global json
        
        jsondata = response.text
        jsondata = jsondata.replace("\r\n","")
        try:
            data = json.loads(jsondata.strip())
        except:
            print (f'JSON Data: {jsondata}')

        data = data['response']['collection'][0]
            
        item['id'] = data['id']
        item['title'] = string.capwords(html.unescape(data['title']))
        item['description'] = html.unescape(data['description'].strip())
        item['date'] = dateparser.parse(data['sites']['collection'][str(item['id'])]['publishDate'].strip()).isoformat()

        item['tags'] = []
        tags = data['tags']['collection']
        for tag in tags:
            tagname = tags[tag]['alias'].strip().title()
            if tagname:
                item['tags'].append(tagname)
        
        item['performers'] = []

        item['url'] = "https://mylifeinmiami.com/scene/" + str(item['id'])
        item['image'] = data['_resources']['primary'][0]['url']
        item['trailer'] = data['_resources']['hoverPreview']
        item['site'] = 'My Life In Miami'
        item['parent'] = 'My Life In Miami'
        item['network'] = 'My Life In Miami'
        
        if self.debug:
            print(item)
        else:
            if item['id'] and item['title']:
                yield item
