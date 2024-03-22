import re
import string
from urllib.parse import urlencode
from slugify import slugify
from tldextract import tldextract
import datetime
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class ProjectOneServicePerformerSpider(BasePerformerScraper):
    name = 'ProjectOneServicePerformer'
    network = 'mindgeek'

    custom_settings = {'CONCURRENT_REQUESTS': '4',
                       # ~ 'AUTOTHROTTLE_ENABLED': 'True',
                       # ~ 'AUTOTHROTTLE_DEBUG': 'False',
                       # ~ 'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '2',
                       }

    start_urls = [
        'https://www.babes.com',
        'https://www.bangbros.com',
        'https://www.biempire.com',
        'https://www.brazzers.com',
        'https://www.bromo.com',
        'https://www.deviante.com',
        'https://www.czechhunter.com/',
        'https://www.digitalplayground.com',
        'https://www.dilfed.com',
        'https://www.erito.com',
        'https://www.fakehub.com',
        'https://www.iconmale.com',
        'https://www.men.com',
        'https://www.metrohd.com',
        'https://www.milehighmedia.com',
        'https://www.milfed.com',
        'https://www.mofos.com',
        'https://www.noirmale.com',
        'https://www.propertysex.com',
        'https://www.realitykings.com',
        'https://www.seancody.com',
        'https://www.sexyhub.com',
        'https://www.squirted.com',
        'https://www.thegayoffice.com',
        'https://www.transangelsnetwork.com',
        'https://www.transharder.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.transsensual.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.trueamateurs.com',
        'https://www.tube8vip.com',
        'https://www.twistys.com',
        'https://www.voyr.com',
        'https://www.whynotbi.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies, meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)

        headers = {
            'instance': token,
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 25
        response.meta['page'] = self.page - 1
        response.meta['url'] = response.url
        return self.get_next_page(response)

    def get_performers(self, response):
        performer_count = 0
        for performer in response.json()['result']:
            item = PerformerItem()
            item['name'] = string.capwords(performer['name'])
            item['gender'] = string.capwords(performer['gender'])
            item['image'] = self.get_image(performer)
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image_blob'] = ""

            if "bio" in performer:
                item['bio'] = performer['bio']
            else:
                item['bio'] = None

            if "birthPlace" in performer:
                item['birthplace'] = performer['birthPlace']
            else:
                item['birthplace'] = None

            if "birthday" in performer:
                item['birthday'] = re.search(r'(\d{4}-\d{2}-\d{2})', performer['birthday']).group(1)
            else:
                item['birthday'] = None

            if "height" in performer:
                item['height'] = str(int(int(performer['height']) * 2.54)) + 'cm'
            else:
                item['height'] = None

            item['weight'] = None

            if "measurements" in performer and re.search(r'(\d+\w+-\d+-\d+)', performer['measurements']):
                item['measurements'] = performer['measurements']
            else:
                item['measurements'] = None

            if "measurements" in performer and re.match(r'\d+\w+', performer['measurements']):
                item['cupsize'] = re.search(r'(\d+\w+)', performer['measurements']).group(1)
            else:
                item['cupsize'] = None

            item['astrology'] = None
            item['fakeboobs'] = None
            item['ethnicity'] = None
            item['nationality'] = None
            item['haircolor'] = None
            item['eyecolor'] = None
            item['tattoos'] = None
            item['piercings'] = None

            if "tags" in performer and len(performer['tags']):
                for tag in performer['tags']:
                    if "Ethnicity" in tag['category']:
                        item['ethnicity'] = tag['name']
                    if "Hair Color" in tag['category']:
                        item['haircolor'] = tag['name']

            item['network'] = 'mindgeek'
            sitename = tldextract.extract(response.meta['url']).domain
            item['url'] = f"https://www.{sitename}.com/model/{performer['id']}/{slugify(item['name'])}"
            performer_count = performer_count + 1
            yield item

        if performer_count > 0:
            if 'page' in response.meta and (
                    response.meta['page'] % response.meta['limit']) < self.limit_pages:
                yield self.get_next_page(response)

    def get_next_page(self, response):
        meta = response.meta

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'lastSceneReleaseDate': f"<{tomorrow}",
            'limit': meta['limit'],
            'orderBy': '-lastSceneReleaseDate',
            'offset': (meta['page'] * meta['limit']),
            'referrer': meta['url'],
        }
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        print('NEXT PAGE: ' + str(meta['page']))
        link = 'https://site-api.project1service.com/v1/actors?' + \
            urlencode(query)
        return scrapy.Request(url=link, callback=self.get_performers, headers=response.meta['headers'], meta=meta)

    def get_token(self, response):
        token = re.search('instance_token=(.+?);', response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, performer):
        image_arr = []
        if 'card_main_rect' in performer['images'] and len(
                performer['images']['card_main_rect']):
            image_arr = performer['images']['card_main_rect']
        elif 'profile' in performer['images'] and len(performer['images']['profile']):
            image_arr = performer['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']
