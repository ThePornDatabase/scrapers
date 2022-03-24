import re
import sys
import warnings
import json
import html
import string
from urllib.parse import urlparse
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class NetworkAdultCentroSpider(BaseSceneScraper):
    name = 'AdultCentro'

    sites = {
        'https://aussiefellatioqueens.com',
        'https://www.mylifeinmiami.com',
        'https://cospimps.com',
        'https://daddyscowgirl.com',
        'https://jerkoffwithme.com',
        'https://kinkyrubberworld.com',
        'https://realagent.xxx',
        'https://facialcasting.com',
        'https://fallinlovia.com',
        'https://bigjohnnyxxx.com',
        'https://dillionation.com',
        'https://isinxxx.com',
        'https://katie71.com',
        'https://peghim.com',
        'https://cleagaultier-official.com',
        'https://danidaniels.com',
        'https://santalatina.com',
        'https://porntugal.com',
        'https://trinitystclair.com',
        'https://aussiexxxhookups.com',
        'https://nordiskaporrfilmer.com',
        'https://ninnworx.com',
        'https://therealscarletred.com',
        'https://psychohenessy.com',
        'https://natashanice.com',
        'https://facialkings.com',
        'https://thiccvision.com',
    }

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
            yield scrapy.Request(link + '/videos/', callback=self.start_requests_2, meta={'link': link})

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

            url = self.get_next_page_url(meta['link'], self.page, meta['token'])
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['token']),
                                     callback=self.parse,
                                     meta=meta)

    def get_next_page_url(self, base, page, token):
        if "sapi" in base:
            uri = urlparse(base)
            base = uri.scheme + "://" + uri.netloc
        page = str((int(page) - 1) * 10)
        if "miami" in base:
            page_url = base + '/sapi/' + token + '/event.last?_method=event.last&offset={}&limit=10&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[showOnHome]=true'
        if "cospimps" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&limit=10&offset={}&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "jerkoff" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "aussiefellatio" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "daddyscowgirl" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "kinkyrubberworld" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "realagent" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[exceptTags]=extra&transitParameters[preset]=videos'
        if "facialcasting" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "fallinlovia" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "bigjohnnyxxx" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "dillionation" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "isinxxx" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-5&fields[0]=generatedContentLink&fields[1]=cName&fields[2]=title&fields[3]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=type&fields[6]=_resources.base.url&fields[7]=_resources.base&fields[8]=length&limit=21&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "natashanice" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[exceptTags]=natashahomemade&transitParameters[preset]=videos'
        if "katie71" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "peghim" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "danidaniels" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[socialParams]=likes&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "santalatina" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "psychohenessy" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "ninnworx" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[socialParams]=likes&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "therealscarletred" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[socialParams]=likes&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "porntugal" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'
        if "trinitystclair" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "aussiexxxhookups" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&limit=10&offset={}&metaFields[totalCount]=1&transitParameters[preset]=videos&transitParameters[v1]=OBoiu4zYsP'
        if "nordiskaporrfilmer" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "cleagaultier" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&class=Adultcentro%5CAmc%5CObject%5CContent&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "facialkings" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-5&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD&transitParameters[preset]=videos'
        if "thiccvision" in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-5&limit=10&offset={}&metaFields[resources][thumb]=baseline.sprite.w225i&metaFields[totalCount]=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=videos'

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
        except:
            print(f'JSON Data: {jsondata}')

        data = data['response']['collection'][0]

        item['id'] = data['id']
        item['title'] = string.capwords(html.unescape(data['title']))
        item['description'] = html.unescape(data['description'].strip())
        item['date'] = dateparser.parse(data['sites']['collection'][str(item['id'])]['publishDate'].strip()).isoformat()

        if "fallinlovia" in response.url:
            item['performers'] = ['Eva Lovia']
        else:
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

        item['url'] = self.format_url(response.url, 'scene/' + str(item['id']))
        item['image'] = data['_resources']['primary'][0]['url'].strip()
        item['image_blob'] = None

        if "cospimps" in response.url:
            item['trailer'] = "https://cospimps.com/api/download/{}/hd1080/stream?video=1".format(item['id'])
        if "facialcasting" in response.url:
            item['trailer'] = "https://facialcasting.com/api/download/{}/hd1080/stream".format(item['id'])
        elif "jerkoff" in response.url:
            item['trailer'] = ''
        else:
            item['trailer'] = data['_resources']['hoverPreview'].strip()

        if not item['trailer']:
            item['trailer'] = ''

        if "aussiefellatio" in response.url:
            item['site'] = 'Aussie Fellatio Queens'
            item['parent'] = 'Aussie Fellatio Queens'
            item['network'] = 'Aussie Fellatio Queens'
            modelurl = "https://aussiefellatioqueens.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "aussiexxxhookups" in response.url:
            item['site'] = 'Aussie XXX Hookups'
            item['parent'] = 'Aussie XXX Hookups'
            item['network'] = 'Aussie XXX Hookups'
            modelurl = "https://aussiexxxhookups.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "kinkyrubberworld" in response.url:
            item['site'] = 'Kinky Rubber World'
            item['parent'] = 'Kinky Rubber World'
            item['network'] = 'Kinky Rubber World'
            modelurl = "https://kinkyrubberworld.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "nordiskaporrfilmer" in response.url:
            item['site'] = 'Svenska Porrfilmer'
            item['parent'] = 'Svenska Porrfilmer'
            item['network'] = 'Svenska Porrfilmer'
            modelurl = "https://nordiskaporrfilmer.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "jerkoff" in response.url:
            item['site'] = 'Jerk Off With Me'
            item['parent'] = 'Jerk Off With Me'
            item['network'] = 'Jerk Off With Me'
            yield item

        if "fallinlovia" in response.url:
            item['site'] = 'Fall in Lovia'
            item['parent'] = 'Fall in Lovia'
            item['network'] = 'Fall in Lovia'
            yield item

        if "dillionation" in response.url:
            item['site'] = 'Dillion Harper'
            item['parent'] = 'Dillion Harper'
            item['network'] = 'Dillion Harper'
            yield item

        if "miami" in response.url:
            item['site'] = 'My Life In Miami'
            item['parent'] = 'My Life In Miami'
            item['network'] = 'My Life In Miami'
            item['performers'] = []
            yield item

        if "daddyscowgirl" in response.url:
            item['site'] = 'Daddys Cowgirl'
            item['parent'] = 'Daddys Cowgirl'
            item['network'] = 'Daddys Cowgirl'
            item['performers'] = []
            yield item

        if "thiccvision" in response.url:
            item['site'] = 'Thiccvision'
            item['parent'] = 'Thiccvision'
            item['network'] = 'Thiccvision'
            item['performers'] = []
            yield item

        if "isinxxx" in response.url:
            item['site'] = 'I Sin XXX'
            item['parent'] = 'I Sin XXX'
            item['network'] = 'I Sin XXX'
            item['performers'] = []
            yield item

        if "cleagaultier" in response.url:
            item['site'] = 'Clea Gaultier'
            item['parent'] = 'Clea Gaultier'
            item['network'] = 'Clea Gaultier'
            item['performers'] = ['Clea Gaultier']
            item['tags'] = []
            yield item

        if "realagent" in response.url:
            item['site'] = 'Real Agent'
            item['parent'] = 'Real Agent'
            item['network'] = 'Real Agent'
            item['performers'] = []
            yield item

        if "trinitystclair" in response.url:
            item['site'] = 'Trinity St Clair'
            item['parent'] = 'Trinity St Clair'
            item['network'] = 'Trinity St Clair'
            modelurl = "https://trinitystclair.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "psychohenessy" in response.url:
            item['site'] = 'Psycho Henessy'
            item['parent'] = 'Psycho Henessy'
            item['network'] = 'Psycho Henessy'
            modelurl = "https://psychohenessy.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "porntugal" in response.url:
            item['site'] = 'Porntugal'
            item['parent'] = 'Porntugal'
            item['network'] = 'Porntugal'
            modelurl = "https://porntugal.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "ninnworx" in response.url:
            item['site'] = 'Ninn Worx'
            item['parent'] = 'Ninn Worx'
            item['network'] = 'Ninn Worx'
            modelurl = "https://ninnworx.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "therealscarletred" in response.url:
            item['site'] = 'Scarlet Red'
            item['parent'] = 'Scarlet Red'
            item['network'] = 'Scarlet Red'
            modelurl = "https://therealscarletred.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "facialkings" in response.url:
            item['site'] = 'Facial Kings'
            item['parent'] = 'Facial Kings'
            item['network'] = 'Facial Kings'
            item['performers'] = []
            yield item

        if "santalatina" in response.url:
            item['site'] = 'Santa Latina'
            item['parent'] = 'Santa Latina'
            item['network'] = 'Santa Latina'
            item['performers'] = []
            yield item

        if "bigjohnnyxxx" in response.url:
            item['site'] = 'Big Johnny XXX'
            item['parent'] = 'Big Johnny XXX'
            item['network'] = 'Big Johnny XXX'
            item['performers'] = []
            yield item

        if "danidaniels" in response.url:
            item['site'] = 'Dani Daniels'
            item['parent'] = 'Dani Daniels'
            item['network'] = 'Dani Daniels'
            item['performers'] = ['Dani Daniels']
            item['tags'] = []
            yield item

        if "peghim" in response.url:
            item['site'] = 'PegHim'
            item['parent'] = 'PegHim'
            item['network'] = 'PegHim'
            item['performers'] = []
            yield item

        if "katie71" in response.url:
            item['site'] = 'Katie71'
            item['parent'] = 'Katie71'
            item['network'] = 'Katie71'
            item['performers'] = ['Katie71']
            yield item

        if "natashanice" in response.url:
            item['site'] = 'Natasha Nice'
            item['parent'] = 'Natasha Nice'
            item['network'] = 'Natasha Nice'
            item['performers'] = ['Natasha Nice']
            yield item

        if "cospimps" in response.url:
            item['site'] = 'Cospimps'
            item['parent'] = 'Cospimps'
            item['network'] = 'Cospimps'
            modelurl = "https://cospimps.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
            meta['item'] = item
            yield scrapy.Request(modelurl, callback=self.get_performers_json, meta=meta)

        if "facialcasting" in response.url:
            item['site'] = 'Facial Casting'
            item['parent'] = 'Facial Casting'
            item['network'] = 'Facial Casting'
            modelurl = "https://facialcasting.com/sapi/{}/model.getModelContent?_method=model.getModelContent&tz=-4&transitParameters[contentId]={}".format(meta['token'], item['id'])
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

        if "psychohenessy" in response.url:
            item['performers'].append('Henessy')

        if "therealscarletred" in response.url:
            item['performers'].append('Scarlet Red')

        if "kinkyrubberworld" in response.url:
            item['performers'].append('Latex Lara')

        if "trinitystclair" in response.url:
            item['performers'].append('Trinity St Clair')

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
            'Kinkyalice',
            'Koneko',
            'Lady Alshari',
            'Lady Estelle',
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
                newlist.append(word)
        return newlist
