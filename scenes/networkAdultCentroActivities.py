import re
import sys
import json
from datetime import datetime
import html
import string
from urllib.parse import urlparse
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkAdultCentroEventsSpider(BaseSceneScraper):
    name = 'AdultCentroEvents'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    sites = [
        ['https://brookelynnebriar.com', '&transitParameters[v1]=a3NPKt70Ku', 'Brookelynne Briar', 'Brookelynne Briar'],
    ]

    selector_map = {
        'external_id': r'scene/(\d+)/',
        'pagination': '/home_page=%s'
    }

    def start_requests(self):
        for link in self.sites:
            yield scrapy.Request(link[0] + '/activity', callback=self.start_requests_2, meta={'link': link[0], 'transit': link[1], 'site': link[2], 'performer': link[3]})

    def start_requests_2(self, response):

        appscript = response.xpath('//script[contains(text(),"fox.createApplication")]/text()').get()
        meta = response.meta
        if meta['link']:
            if appscript:
                ah = re.search(r'"ah":"(.*?)"', appscript).group(1)
                aet = re.search(r'"aet":([0-9]+?),', appscript).group(1)
                if ah and aet:
                    # ~ print(f'ah: {ah}')
                    # ~ print(f'aet: {aet}')
                    token = ah[::-1] + "/" + str(aet)
                    # ~ print(f'Token: {token}')

            if not token:
                sys.exit()
            else:
                meta['token'] = token

            url = self.get_next_page_url(meta['link'], self.page, meta['token'], meta['transit'], datetime.today().strftime('%Y-%m-%d'))
            meta['page'] = self.page
            yield scrapy.Request(url, callback=self.parse, meta=meta)

    def parse(self, response, **kwargs):
        meta = response.meta
        jsondata = response.json()
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if len(jsondata['response']['collection']):
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                if jsondata['response']['meta']['hasPrev'] == "true" or jsondata['response']['meta']['hasPrev']:
                    max_date = re.search(r'(\d{4}-\d{2}-\d{2})', jsondata['response']['meta']['minDate']).group(1)
                    yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['token'], meta['transit'], max_date), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, token, transit, max_date):
        if "sapi" in base:
            uri = urlparse(base)
            base = uri.scheme + "://" + uri.netloc

        page_url = base + '/sapi/' + token + f'/Activity_Event.get?_method=Activity_Event.get&tz=-4&date={max_date}%2013%3A00%3A00&direction=prev&types[1]=1&types[2]=1&types[3]=0&types[4]=0&types[5]=1&types[6]=1&types[7]=1&limit=9&returnNewFormat=true{transit}'
        return self.format_url(base, page_url.format(page))

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']
        for scene in jsondata:
            if "miami" in response.url or "brookelynn" in response.url:
                scene_id = scene['_typedParams']['id']
            else:
                scene_id = scene['id']
            scene_url = f"https://brookelynnebriar.com/sapi/{meta['token']}/content.load?_method=content.load&tz=-4&filter[id][fields][0]=id&filter[id][values][0]={scene_id}&limit=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[preset]=scene"
            if "class" not in scene['_typedParams'] or scene['_typedParams']['class'].lower() != "liveshow":
                yield scrapy.Request(scene_url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

        jsondata = response.text
        jsondata = jsondata.replace('\r\n', '')
        try:
            data = json.loads(jsondata.strip())
        except Exception as ex:
            print(f'Exception: {ex} --> JSON Data: {jsondata}')

        if data and "response" in data and len(data['response']['collection']):
            data = data['response']['collection'][0]

            item['id'] = data['id']
            item['title'] = unidecode.unidecode(html.unescape(string.capwords(data['title']).strip()))
            item['description'] = html.unescape(data['description'].strip())
            item['date'] = self.parse_date(data['sites']['collection'][str(item['id'])]['publishDate'].strip()).isoformat()
            item['performers'] = []
            item['tags'] = []
            if data['length']:
                item['duration'] = data['length']

            tags = data['tags']['collection']
            for tag in tags:
                tagname = tags[tag]['alias'].strip().title()
                if tagname and "Model - " not in tagname:
                    item['tags'].append(tagname)
            item['tags'] = self.clean_tags(item['tags'])

            item['url'] = self.format_url(response.url, 'scene/' + str(item['id']))
            item['image'] = data['_resources']['primary'][0]['url'].strip()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ''

            if 'site' in meta and meta['site']:
                item['site'] = meta['site']
                item['parent'] = meta['site']
                item['network'] = meta['site']
                modelurl = meta['link'] + "/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
                meta['item'] = item
                yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

    def get_performers_json(self, response):
        meta = response.meta
        item = meta['item']

        jsontext = response.text
        performers = re.findall('stageName\":\"(.*?)\"', jsontext)
        if performers:
            item['performers'] = performers
        else:
            item['performers'] = []

        if "sukmydick" in response.url:
            item['performers'] = []
        if "lonelymeow" in response.url:
            item['performers'] = ['LonelyMeow']
        if "sallydangelo" in response.url:
            item['performers'] = ['Sally DAngelo']

        if "Don Whoe" in item['tags']:
            item['tags'].remove("Don Whoe")
            item['performers'].append("Don Whoe")
        if "Lisa Rivera" in item['tags']:
            item['tags'].remove("Lisa Rivera")
            item['performers'].append("Lisa Rivera")
        if "idreamofjo" in response.url and "Jo" in item['performers']:
            item['performers'].remove("Jo")
        if "Nina Rivera" in item['tags']:
            item['tags'].remove("Nina Rivera")
            item['performers'].append("Nina Rivera")
        if "Nadia White" in item['tags']:
            item['tags'].remove("Nadia White")
            item['performers'].append("Nadia White")
        if "Don And Lisa" in item['tags']:
            item['tags'].remove("Don And Lisa")
        if "Don And Nina" in item['tags']:
            item['tags'].remove("Don And Nina")
        if "Nina And Don" in item['tags']:
            item['tags'].remove("Nina And Don")

        if "antonioclemens" in response.url:
            for tag in item['tags']:
                if "model" in tag:
                    item['tags'].remove(tag)

        if item['performers']:
            for performer in item['performers']:
                if performer in item['tags']:
                    item['tags'].remove(performer)
                if performer.lower() in item['tags']:
                    item['tags'].remove(performer.lower())

        if meta['performer'] and meta['performer'] not in item['performers']:
            item['performers'].append(meta['performer'])

        yield self.check_item(item, self.days)

    def clean_tags(self, tags):
        cleanlist = [
            'Latex Lara',
            'Latex Lea',
            'Nadira Diamond',
            'Lola_Noir',
            'Freja Dottier',
            'Kinky Alice',
            'Nyxi_Leon',
            'Anita Divina',
            'Anitadivana',
            'Bizarr',
            'Bizarrlady Estelle',
            'Constace Chaos',
            'Constance Chaos',
            'Constancechaos',
            'Courtney Morgan',
            'Courtneymorgan',
            'Daniela Benatta',
            'Danielabenatta',
            'Ezada Sinn',
            'Ezada',
            'Ezadasinn',
            'Frejadottir',
            'Freja_Dottir',
            'Freya',
            'Goddess Ezada',
            'Goddess Maya',
            'Governess Painless',
            'Governesspainless',
            'Jazziemania',
            'Jazzieque',
            'Jazziequexxx',
            'Jacquelynjaxx',
            'Kinkyalice',
            'Koneko',
            'Lady Alshari',
            'Lady Estelle',
            'Lady Sublime',
            'Ladyalshari',
            'Ladyluciana',
            'Lara',
            'Latex Lucy',
            'Lil Candy',
            'Lilcandy',
            'Lucy',
            'Miss Courtney',
            'Misscourtney',
            'Misswhitneymorgan',
            'Mistress Courtney',
            'Mistress Ezada',
            'Mistresscourtney',
            'Mistressluciana',
            'Request',
            'Rubber_Jeff',
            'Whitney Morgan',
        ]
        newlist = []
        for word in tags:
            if word not in cleanlist:
                if not re.search(r'(\d{4})', word):
                    matches = ['dani ', 'deni ', 'daniel', 'deniels', 'kaite']
                    if any(x in word.lower() for x in matches):
                        word = ''
                    else:
                        newlist.append(word)
        return newlist
