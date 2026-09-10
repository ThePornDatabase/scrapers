import re
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
        ## ['https://andreagarcia.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Andrea Garcia', 'Andrea Garcia'],
        ## ['https://cleagaultier-official.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Clea Gaultier', 'Clea Gaultier'],
        ## ['https://dripdropprod.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'DripDrop', ''],
        ## ['https://facialkings.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Facial Kings', ''],
        ## ['https://iadorejessicacho.live', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'I Adore Jessica Cho', 'Jessica Cho'],
        ## ['https://idreamofjo.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'I Dream of Jo', 'Monica Sweet'],
        ## ['https://katie71.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Katie71', 'Katie71'],
        ## ['https://ponygirl-riding.com', '&transitParameters[v1]=OBoiu4zYsP&transitParameters[v2]=OhUOlmasXD', 'Ponygirl Riding', ''],
        ## ['https://pvgirls.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Porn Valley Girls', ''],
        ## ['https://trinitystclair.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Trinity St Clair', 'Trinity St Clair'],  # Site non-responsive (2022-08-01)
        ## ['https://www.crystaldenison.com', '&transitParameters[v1]=OBoiu4zYsP', 'Crystal Denison', 'Crystal Denison'],
        ## ['https://www.esperanzaplus.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Esperanza Plus', 'Esperanza Gomez'],
        ## ['https://www.gingerfans.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Ginger Fans', 'Ginger St Cyr'],
        ## ['https://www.honeygoldxxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Honey Gold', 'Honey Gold'],  # Site non-responsive (2022-08-01)
        ## ['https://www.jazziequexxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Jazzie Que XXX', 'Jacquelyn Jaxx'],
        ## ['https://www.ladyfoxxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Lady Foxxx', 'Lisa Fox'],
        ## ['https://www.naughtyayla.com', '&transitParameters[v1]=OBoiu4zYsP', 'Naughty Ayla', 'Naughty Ayla'],
        ## ['https://www.nudechrissy.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Nude Chrissy', ''],
        ## ['https://www.patriciagoddess.com', '&transitParameters[v1]=uaKV7hnDcF', 'Patricia Goddess', 'Patricia Goddess'],
        ## ['https://www.sabrinasabrokvideos.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Sabrina Sabrok', 'Sabrina Sabrok'],
        ## ~ # ['https://bruceandmorgan.net', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Bruce and Morgan', ''],  Closed site, historical only
        ##['https://ninnworx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Ninn Worx', ''],
        ['https://aikoprincess.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Aiko Princess', ''],
        ['https://allofaveryjane.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'All of Avery Jane', 'Avery Jane'],
        ['https://antonioclemens.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Antonio Clemens', ''],
        ['https://arabellesplayground.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Arabelles Playground', ''],
        ['https://aussiefellatioqueens.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Aussie Fellatio Queens', ''],
        ['https://aussiexxxhookups.com', '&transitParameters[v1]=OBoiu4zYsP', 'Aussie XXX Hookups', ''],
        ['https://bhalasada.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bhala Sada', ''],
        ['https://bigjohnnyxxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Big Johnny XXX', ''],
        ['https://brookelynnebriar.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Brookelynne Briar', 'Brookelynne Briar'],
        ['https://bunnyscout.tv', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bunny Scout', ''],
        ['https://clubcuck.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Club Cuck', 'Club Cuck'],
        ['https://clubmaseratixxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Club Maserati XXX', ''],
        ['https://cospimps.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Cospimps', ''],
        ['https://daddyscowgirl.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Daddys Cowgirl', ''],
        ['https://dakotamarr.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Dakota Marr', ''],
        ['https://danidaniels.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Dani Daniels', 'Dani Daniels'],
        ['https://dillionation.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Dillion Harper', 'Dillion Harper'],
        ['https://exploitedtalent.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Exploited Talent', ''],
        ['https://facialcasting.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Facial Casting', ''],
        ['https://fallinlovia.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Fall in Lovia', 'Eva Lovia'],
        ['https://ginagerson.xxx', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Gina Gerson', ''],
        ['https://hansthehornygrandpa.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Hans The Horny Grandpa', ''],
        ['https://hunglow.org', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Hung Low', 'Hung Lo'],
        ['https://isinxxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'I Sin XXX', ''],
        ['https://jenysmith.net', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Jeny Smith', 'Jeny Smith'],
        ['https://jerkoffwithme.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Jerk Off With Me', ''],
        ['https://jessydubairaw.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Jessy Dubai Raw', 'Jessy Dubai'],
        ['https://kinkyrubberworld.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Kinky Rubber World', 'Latex Lara'],
        ['https://lilcandy.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Lil Candy', 'Lil Candy'],
        ['https://lonelymeow.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'LonelyMeow', ''],
        ['https://mma-xxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'MMA XXX', ''],
        ['https://mugursworld.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Mugur Porn', ''],
        ['https://natashanice.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Natasha Nice', 'Natasha Nice'],
        ['https://nordiskaporrfilmer.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Svenska Porrfilmer', ''],
        ['https://oopsmodels.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Oops Models (Official)', ''],
        ['https://pastelgoddess.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Pastel Goddess', 'Pastel Goddess'],
        ['https://peghim.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'PegHim', ''],
        ['https://porntugal.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Porntugal', ''],
        ['https://psychohenessy.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Psycho Henessy', 'Henessy'],
        ['https://realagent.xxx', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Real Agent', ''],
        ['https://rydenarmani.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Ryden Armani', ''],
        ['https://sallydangeloxxx.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Sally Dangelo XXX', ''],
        ['https://santalatina.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Santa Latina', ''],
        ['https://slobjobz.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'SlobJobz', ''],
        ['https://sukmydick.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Suk My Dick', ''],
        ['https://suzyq.modelcentro.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'SuzyQ', 'SuzyQ'],
        ['https://thepervempire.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'The Perv Empire', ''],
        ## ['https://therealscarletred.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Scarlet Red', 'Scarlet Red'],
        ['https://thiccvision.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Thiccvision', ''],
        ['https://transtakenraw.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Trans Taken', ''],
        ['https://vinaskyxxx.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Vina Sky', ''],
        ['https://www.amberspanks.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Amber Spanks', 'Amber Dawn'],
        ['https://www.backalleytoonzonline.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Back Alley Toonz', ''],
        ['https://www.baileyrayne.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Bailey Rayne', 'Bailey Rayne'],
        ['https://www.frdiapergirls.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'French Diaper Girls', ''],
        ['https://www.getyourkneesdirty.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Get Your Knees Dirty', ''],
        ['https://www.hollandswing.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Holland Swing', 'Nikki Holland'],
        ['https://www.kelleycabbana.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Kelley Cabbana', 'Kelley Cabbana'],
        ['https://www.ladysublime.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Lady Sublime', 'Lady Sublime'],
        ['https://www.lalaiveyxxx.com', '&transitParameters[v1]=OBoiu4zYsP', 'La La Ivey XXX', 'La La Ivey'],
        ['https://www.matthiaschrist.com', '&transitParameters[v1]=OBoiu4zYsP', 'Matthias Christ', ''],
        ['https://www.monstermalesprod.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Monster Males Productions', ''],
        ['https://www.mylifeinmiami.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'My Life In Miami', ''],
        ['https://www.niksindian.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Niks Indian', ''],
        ['https://www.primalbang.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Primal Bang', ''],
        ['https://www.throatwars.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Throat Wars', ''],
        ['https://www.ticklehotness.com', '&transitParameters[v1]=OhUOlmasXD&transitParameters[v2]=OhUOlmasXD', 'Tickle Hotness', ''],
        ['https://www.viscontivip.com', '&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD', 'Visconti VIP', ''],
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

    async def start(self):
        for link in self.sites:
            print(f'Fetching scenes from {link[2]}')
            yield scrapy.Request(link[0] + '/videos/', callback=self.start_requests_2, meta={'link': link[0], 'transit': link[1], 'site': link[2], 'performer': link[3]})

    def start_requests_2(self, response):
        """Build the per-site API token out of the inline fox application config.

        Several of the configured domains no longer serve their own tour -- they
        redirect to another site, or in one case to google.com -- so the fox script
        is absent and no token can be built.  That used to leave `token` unbound
        (crashing the callback) or hit sys.exit(), which killed the whole crawl and
        took every still-working site down with it.  Such a site is now skipped.
        """
        meta = self.copy_meta(response)
        if not meta['link']:
            return

        appscript = response.xpath('//script[contains(text(),"fox.createApplication")]/text()').get()
        ah = re.search(r'"ah":"(.*?)"', appscript) if appscript else None
        aet = re.search(r'"aet":([0-9]+?),', appscript) if appscript else None
        if not (ah and aet):
            self.logger.warning('No fox application token on %s (redirected to %s) - skipping %s',
                                meta['link'], response.url, meta['site'])
            return

        meta['token'] = ah.group(1)[::-1] + "/" + str(aet.group(1))
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
                meta = self.copy_meta(response)
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
        if "brookelynn" in base:
            page_url = base + '/sapi/' + token + '/event.last?_method=event.last&tz=-4&limit=10&offset={}&transitParameters[showOnHome]=true' + transit
        elif 'mylifeinmiami' in base:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&transitParameters[preset]=scene' + transit
        else:
            page_url = base + '/sapi/' + token + '/content.load?_method=content.load&tz=-4&limit=10&offset={}&transitParameters[preset]=videos' + transit

        url = self.format_url(base, page_url.format(page))
        return url

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']

        for scene in jsondata:
            if "brookelynn" in response.url:
                scene_id = scene['_typedParams']['id']
            else:
                scene_id = scene['id']
            scene_url = self.format_url(response.url, '/sapi/' + meta['token'] + '/content.load?_method=content.load&tz=-4&filter[id][fields][0]=id&filter[id][values][0]=%s&limit=1&transitParameters[v1]=ykYa8ALmUD&transitParameters[preset]=scene' % scene_id)
            yield scrapy.Request(scene_url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)

    def parse_scene(self, response):
        meta = self.copy_meta(response)
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

            if "jerkoff" in response.url or "dillionation" in response.url:
                performers = data['tags']['collection']
                for performer in performers:
                    # Some sites (mugursworld) hand back a numeric alias
                    performername = str(performers[performer].get('alias') or '').strip().title()
                    if performername:
                        item['performers'].append(performername)
            elif "daddyscowgirl" not in response.url and "fallinlovia" not in response.url:
                tags = data['tags']['collection']
                for tag in tags:
                    tagname = str(tags[tag].get('alias') or '').strip().title()
                    if tagname and "Model - " not in tagname:
                        item['tags'].append(tagname)
                item['tags'] = self.clean_tags(item['tags'])

            if "arabelle" in response.url:
                meta['performer'] = "Arabelle Raphael"

            if "dakotamarr" in response.url:
                meta['performer'] = "Dakota Marr"

            if "vinasky" in response.url:
                meta['performer'] = "Vina Sky"

            if "aikoprincess" in response.url:
                meta['performer'] = "Aiko Moe"

            if "ginagerson" in response.url:
                meta['performer'] = "Gina Gerson"

            if "clubmaseratixxx" in response.url:
                meta['performer'] = "Maserati XXX"

            if "rydenarmani" in response.url:
                meta['performer'] = "Ryden Armani"

            if "slobjobz" in response.url:
                item['tags'].append("Blowjob")

            if "mugursworld" in response.url:
                meta['performer'] = "Mugur"

            if "backalleytoonz" in response.url:
                item['tags'].append("Animation")

            if "frdiapergirls" in response.url:
                item['tags'].append("Diapers")

            if "clubcuck" in response.url:
                item['tags'].append("Cuckold")
                item['tags'].append("Interracial")
                if "Club Cuck" in item['performers']:
                    item['performers'].remove("Club Cuck")

            if "hansthehornygrandpa" in response.url:
                item['tags'].append("Older / Younger")

            if "ponygirl" in response.url:
                item['tags'].append("Ponygirl")
                item['tags'].append("Fetish")

            if "getyourkneesdirty" in response.url:
                item['tags'].append("Blowjob")

            if "lonelymeow" in response.url:
                item['tags'].append("Asian")

            if "mma-xxx" in response.url:
                item['tags'].append("Wrestling")

            if "throatwars" in response.url:
                item['tags'].append("Interracial")
                item['tags'].append("Blowjob")
                item['tags'].append("Face Fuck")
                item['tags'].append("Deepthroat")

            if "oopsmodels" in response.url:
                item['tags'] = []

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
        meta = self.copy_meta(response)
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
        if "Dakota Marr" in item['tags']:
            item['tags'].remove("Dakota Marr")
        if "idreamofjo" in response.url and "Jo" in item['performers']:
            item['performers'].remove("Jo")
        if "Nina Rivera" in item['tags']:
            item['tags'].remove("Nina Rivera")
            item['performers'].append("Nina Rivera")
        if "French Diaper Girls" in item['performers']:
            item['performers'].remove("French Diaper Girls")            
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
            'French Diaper Girls',
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
