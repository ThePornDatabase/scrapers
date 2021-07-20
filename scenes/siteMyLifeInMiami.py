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

    def start_requests(self):
        
        yield scrapy.Request("https://www.mylifeinmiami.com/videos", callback=self.start_requests_2, cookies={'splash':'1'})
        
    def start_requests_2(self, response):
        meta = {}
        
        appscript = response.xpath('//script[contains(text(),"fox.createApplication")]/text()').get()
        if appscript:
            ah = re.search('\"ah\":\"(.*?)\"', appscript).group(1)
            aet = re.search('\"aet\":(\d+?),', appscript).group(1)
            if ah and aet:
                print(f'ah: {ah}')
                print(f'aet: {aet}')
                token = ah[::-1] + "/" + str(aet)
                print(f'Token: {token}')
                
        if not token:
            quit()
        else:
            meta['token'] = token
            
        for link in self.start_urls:
            url = url=self.get_next_page_url(link, self.page, meta['token'])
            meta['page'] = self.page
            yield scrapy.Request(url,
                                 callback=self.parse,
                                 meta=meta,
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['token']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, token):
        page = str((int(page)-1) * 10)
        page_url = "https://mylifeinmiami.com/sapi/" + token + "/event.last?_method=event.last&offset=%s&limit=10&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[showOnHome]=true"
        return self.format_url(base, page_url % page)


    def get_scenes(self, response):
        meta = response.meta
        global json
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']
        
        for scene in jsondata:
            scene_id = scene['_typedParams']['id']
            scene_url = "https://mylifeinmiami.com/sapi/" + meta['token'] + "/content.load?_method=content.load&tz=-4&filter[id][fields][0]=id&filter[id][values][0]=%s&limit=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[preset]=scene" % scene_id
            yield scrapy.Request(scene_url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)


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
