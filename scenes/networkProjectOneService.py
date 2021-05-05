import re
from urllib.parse import urlencode
import dateparser
import datetime
import scrapy
from slugify import slugify
from tldextract import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ProjectOneServiceSpider(BaseSceneScraper):
    name = 'ProjectOneService'
    network = 'mindgeek'

    start_urls = [
        'https://www.8thstreetlatinas.com',
        'https://www.babes.com',
        'https://www.bellesafilms.com',
        'https://www.biempire.com',
        'https://www.brazzers.com',
        'https://www.bromo.com',
        'https://www.deviante.com',
        'https://www.devianthardcore.com',
        'https://www.digitalplayground.com',
        'https://www.doghousedigital.com',
        'https://www.dontbreakme.com',
        'https://www.erito.com',
        'https://www.fakehub.com',
        'https://www.familyhookups.com',
        'https://www.familysinners.com',
        'https://www.girlgrind.com',
        'https://www.iconmale.com',
        'https://www.iknowthatgirl.com',
        'https://www.lesbea.com',
        'https://www.letstryanal.com',
        'https://www.lilhumpers.com',
        'https://www.lookathernow.com',
        'https://www.men.com',
        'https://www.metrohd.com',
        'https://www.milehighmedia.com',
        'https://www.milfed.com',
        'https://www.milfhunter.com',
        'https://www.mofos.com',
        'https://www.propertysex.com',
        'https://www.publicagent.com',
        'https://www.publicpickups.com',
        'https://www.realityjunkies.com',
        'https://www.realitykings.com',
        'https://www.sexyhub.com',
        'https://www.sneakysex.com',
        'https://www.squirted.com',
        'https://www.sweetheartvideo.com',
        'https://www.sweetsinner.com',
        'https://www.thegayoffice.com',
        'https://www.transangels.com',
        'https://www.transangelsnetwork.com',
        'https://www.transharder.com',
        'https://www.transsensual.com',
        'https://www.trueamateurs.com',
        'https://www.tube8vip.com',
        'https://www.twistys.com',
        'https://www.welivetogether.com',
        'https://www.whynotbi.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies,
                                 meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)

        headers = {
            'instance': token,
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 100
        response.meta['page'] = -1
        response.meta['url'] = response.url

        return self.get_next_page(response)

    def get_scenes(self, response):
        scene_count = 0

        for scene in response.json()['result']:
            item = SceneItem()

            if scene['collections'] and len(scene['collections']):
                item['site'] = scene['collections'][0]['name']
            else:
                item['site'] = tldextract.extract(response.meta['url']).domain

            if tldextract.extract(
                    response.meta['url']).domain == 'digitalplayground':
                item['site'] = 'digitalplayground'

            item['image'] = self.get_image(scene)
            item['trailer'] = self.get_trailer(scene)
            item['date'] = dateparser.parse(scene['dateReleased']).isoformat()
            item['id'] = scene['id']
            item['network'] = self.network
            item['parent'] = item['site']

            if 'title' in scene:
                item['title'] = scene['title']
            else:
                item['title'] = item['site'] + ' ' + \
                                dateparser.parse(scene['dateReleased']
                                                 ).strftime('%b/%d/%Y')

            if 'description' in scene:
                item['description'] = scene['description']
            else:
                item['description'] = ''

            item['performers'] = []
            for model in scene['actors']:
                item['performers'].append(model['name'])

            if 'actors' not in scene or len(item['performers']) is 0:
                item['performers'] = ['Unknown']

            item['tags'] = []
            for tag in scene['tags']:
                item['tags'].append(tag['name'])

            path = '/scene/' + str(item['id']) + '/' + slugify(item['title'])
            item['url'] = self.format_url(response.meta['url'], path)
            
            # Deviante abbreviations
            if item['site'] == "fmf":
                item['site'] = "Forgive Me Father"
            if item['site'] == "sw":
                item['site'] = "Sex Working"
            if item['site'] == "pdt":
                item['site'] = "Pretty Dirty Teens"
            if item['site'] == "lha":
                item['site'] = "Love Her Ass"
            if item['site'] == "es":
                item['site'] = "Erotic Spice"

            scene_count = scene_count + 1

            yield item

        if scene_count > 0:
            if 'page' in response.meta and (response.meta['page'] % response.meta['limit']) < self.limit_pages:
                yield self.get_next_page(response)

    def get_next_page(self, response):
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'dateReleased': f"<{tomorrow}",
            'limit': meta['limit'],
            'type': 'scene',
            'orderBy': '-dateReleased',
            'offset': (meta['page'] * meta['limit']),
            'referrer': meta['url'],
        }

        print('NEXT PAGE: ' + str(meta['page']))

        link = 'https://site-api.project1service.com/v2/releases?' + urlencode(query)
        return scrapy.Request(url=link, callback=self.get_scenes, headers=response.meta['headers'], meta=meta)

    def get_token(self, response):
        token = re.search('instance_token=(.+?);',
                          response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, scene):
        image_arr = []
        if 'card_main_rect' in scene['images'] and len(
                scene['images']['card_main_rect']):
            image_arr = scene['images']['card_main_rect']
        elif 'poster' in scene['images'] and len(scene['images']['poster']):
            image_arr = scene['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']

    def get_trailer(self, scene):
        for index in scene['videos']:
            trailer = scene['videos'][index]
            for size in ['720p', '576p', '480p', '360p', '1080p', '4k']:
                if size in trailer['files']:
                    return trailer['files'][size]['urls']['view']
