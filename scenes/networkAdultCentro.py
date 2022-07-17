import re
import sys
import json
import html
import string
from urllib.parse import urlparse
import unidecode
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkAdultCentroSpider(BaseSceneScraper):
    name = 'AdultCentro'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    sites = [
        ['https://allofaveryjane.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'All of Avery Jane', 'Avery Jane'],
        ['https://www.amberspanks.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Amber Spanks', 'Amber Dawn'],
        ['https://andreagarcia.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Andrea Garcia', 'Andrea Garcia'],
        ['https://aussiefellatioqueens.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Aussie Fellatio Queens', ''],
        ['https://www.baileyrayne.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bailey Rayne', 'Bailey Rayne'],
        ['https://aussiexxxhookups.com', '&transitParameters[v1]=OBoiu4zYsP', 'Aussie XXX Hookups', ''],
        ['https://www.backalleytoonzonline.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Back Alley Toonz', ''],
        ['https://bhalasada.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bhala Sada', ''],
        ['https://bigjohnnyxxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Big Johnny XXX', ''],
        ['https://brookelynnebriar.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Brookelynne Briar', 'Brookelynne Briar'],
        # ['https://bruceandmorgan.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Bruce and Morgan', ''],  Closed site, historical only
        ['https://bunnyscout.tv', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bunny Scout', ''],
        ['https://cleagaultier-official.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Clea Gaultier', 'Clea Gaultier'],
        ['https://cospimps.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Cospimps', ''],
        ['https://daddyscowgirl.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Daddys Cowgirl', ''],
        ['https://danidaniels.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Dani Daniels', 'Dani Daniels'],
        ['https://dillionation.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Dillion Harper', 'Dillion Harper'],
        ['https://www.esperanzaplus.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Esperanza Plus', 'Esperanza Gomez'],
        ['https://facialcasting.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Facial Casting', ''],
        ['https://facialkings.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Facial Kings', ''],
        ['https://fallinlovia.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Fall in Lovia', 'Eva Lovia'],
        ['https://www.hollandswing.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Holland Swing', 'Nikki Holland'],
        ['https://www.honeygoldxxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Honey Gold', 'Honey Gold'],
        ['https://isinxxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'I Sin XXX', ''],
        ['https://jerkoffwithme.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Jerk Off With Me', ''],
        ['https://katie71.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Katie71', 'Katie71'],
        ['https://www.kelleycabbana.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Kelley Cabbana', 'Kelley Cabbana'],
        ['https://kinkyrubberworld.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Kinky Rubber World', 'Latex Lara'],
        ['https://www.ladysublime.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Lady Sublime', 'Lady Sublime'],
        ['https://www.matthiaschrist.com', '&transitParameters[v1]=OBoiu4zYsP', 'Matthias Christ', ''],
        ['https://www.monstermalesprod.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Monster Males Productions', ''],
        ['https://natashanice.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Natasha Nice', 'Natasha Nice'],
        ['https://www.crystaldenison.com', '&transitParameters[v1]=OBoiu4zYsP', 'Crystal Denison', 'Crystal Denison'],
        ['https://www.gingerfans.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Ginger Fans', 'Ginger St Cyr'],
        ['https://iadorejessicacho.live', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'I Adore Jessica Cho', 'Jessica Cho'],
        ['https://www.jazziequexxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Jazzie Que XXX', 'Jacquelyn Jaxx'],
        ['https://www.ladyfoxxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Lady Foxxx', 'Lisa Fox'],
        ['https://www.lalaiveyxxx.com', '&transitParameters[v1]=OBoiu4zYsP', 'La La Ivey XXX', 'La La Ivey'],
        ['https://www.naughtyayla.com', '&transitParameters[v1]=OBoiu4zYsP', 'Naughty Ayla', 'Naughty Ayla'],
        ['https://www.patriciagoddess.com', '&transitParameters[v1]=uaKV7hnDcF', 'Patricia Goddess', 'Patricia Goddess'],
        ['https://ninnworx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Ninn Worx', ''],
        ['https://nordiskaporrfilmer.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Svenska Porrfilmer', ''],
        ['https://www.nudechrissy.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Nude Chrissy', ''],
        ['https://peghim.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'PegHim', ''],
        ['https://porntugal.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Porntugal', ''],
        ['https://www.primalbang.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Primal Bang', ''],
        ['https://psychohenessy.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Psycho Henessy', 'Henessy'],
        ['https://realagent.xxx', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Real Agent', ''],
        ['https://www.sabrinasabrokvideos.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Sabrina Sabrok', 'Sabrina Sabrok'],
        ['https://santalatina.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Santa Latina', ''],
        ['https://sukmydick.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Suk My Dick', ''],
        ['https://therealscarletred.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Scarlet Red', 'Scarlet Red'],
        ['https://thiccvision.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Thiccvision', ''],
        ['https://www.ticklehotness.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Tickle Hotness', ''],
        ['https://trinitystclair.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Trinity St Clair', 'Trinity St Clair'],
        ['https://www.viscontivip.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Visconti VIP', ''],
        ['https://www.mylifeinmiami.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'My Life In Miami', ''],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'scene/(\d+)/',
        'pagination': '/home_page=%s'
    }

    def start_requests(self):
        for link in self.sites:
            yield scrapy.Request(link[0] + '/videos/', callback=self.start_requests_2, meta={'link': link[0], 'transit': link[1], 'site': link[2], 'performer': link[3]})

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

            url = self.get_next_page_url(meta['link'], self.page, meta['token'], meta['transit'])
            meta['page'] = self.page
            yield scrapy.Request(url, callback=self.parse, meta=meta)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['token'], meta['transit']),
                                     callback=self.parse,
                                     meta=meta)

    def get_next_page_url(self, base, page, token, transit):
        if "sapi" in base:
            uri = urlparse(base)
            base = uri.scheme + "://" + uri.netloc
        page = str((int(page) - 1) * 10)
        if 'mylifeinmiami' in base:
            page_url = base + '/sapi/' + token + '/event.last?_method=event.last&tz=-4&limit=10&offset={}&transitParameters[showOnHome]=true' + transit
        else:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&transitParameters[preset]=videos' + transit

        return self.format_url(base, page_url.format(page))

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']

        for scene in jsondata:
            if "miami" in response.url:
                scene_id = scene['_typedParams']['id']
            else:
                scene_id = scene['id']
            scene_url = self.format_url(response.url, '/sapi/' + meta['token'] + '/content.load?_method=content.load&tz=-4&filter[id][fields][0]=id&filter[id][values][0]=%s&limit=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[preset]=scene' % scene_id)
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

        data = data['response']['collection'][0]

        item['id'] = data['id']
        item['title'] = unidecode.unidecode(html.unescape(string.capwords(data['title']).strip()))
        item['description'] = html.unescape(data['description'].strip())
        item['date'] = self.parse_date(data['sites']['collection'][str(item['id'])]['publishDate'].strip()).isoformat()
        item['performers'] = []
        item['tags'] = []

        if "jerkoff" in response.url or "dillionation" in response.url:
            performers = data['tags']['collection']
            for performer in performers:
                performername = performers[performer]['alias'].strip().title()
                if performername:
                    item['performers'].append(performername)
        elif "daddyscowgirl" not in response.url and "fallinlovia" not in response.url:
            tags = data['tags']['collection']
            for tag in tags:
                tagname = tags[tag]['alias'].strip().title()
                if tagname and "Model - " not in tagname:
                    item['tags'].append(tagname)
            item['tags'] = self.clean_tags(item['tags'])

        if "backalleytoonz" in response.url:
            item['tags'].append("Animation")

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
            if "Don Whoe" in item['tags']:
                item['tags'].remove("Don Whoe")
                item['performers'].append("Don Whoe")
            if "Lisa Rivera" in item['tags']:
                item['tags'].remove("Lisa Rivera")
                item['performers'].append("Lisa Rivera")
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

        if item['performers']:
            for performer in item['performers']:
                if performer in item['tags']:
                    item['tags'].remove(performer)
                if performer.lower() in item['tags']:
                    item['tags'].remove(performer.lower())

        if meta['performer'] and meta['performer'] not in item['performers']:
            item['performers'].append(meta['performer'])

        yield item

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
            'Lucy',
            'Miss Courtney',
            'Misscourtney',
            'Misswhitneymorgan',
            'Mistress Courtney',
            'Mistress Ezada',
            'Mistresscourtney',
            'Mistressluciana',
            'Rubber_Jeff',
            'Whitney Morgan'
        ]
        newlist = []
        for word in tags:
            if word not in cleanlist:
                matches = ['dani ', 'deni ', 'daniel', 'deniels', 'kaite']
                if any(x in word.lower() for x in matches):
                    word = ''
                else:
                    newlist.append(word)
        return newlist
