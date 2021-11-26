import re
from datetime import date, timedelta
import json
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class TeenCoreClubSpider(BaseSceneScraper):
    name = 'TeenCoreClub'
    network = 'Teen Core Club'
    parent = 'Teen Core Club'

    # Note: These scenes could all have been pulled from one API location, but the returned JSON doesn't include any
    #       site or category information, so I needed to split them up like this to return the associated site per scene
    #       I checked available scenes as of writing and there were not any duplicate ids between sites

    start_urls = [
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=178&genre=0', 'Analyzed Girls'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=180&genre=0', 'Ass Teen Mouth'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=182&genre=0', 'Bang Teen Pussy'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=184&genre=0', 'Brutal Invasion'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=362&genre=0', 'Clean My Ass'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=278&genre=0', 'College Party Time'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=186&genre=0', 'Cumaholic Teens'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=280&genre=0', 'Cum Filled Throat'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=362&genre=0', 'CumSumption Cocktail'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=188&genre=0', 'Defiled18'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=284&genre=0', 'Dirty Babysitter'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=190&genre=0', 'Double Teamed Teens'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=192&genre=0', 'Dream Teens HD'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=288&genre=0', 'Drilled Chicks'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=290&genre=0', 'Dual Throat'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=292&genre=0', 'Gang Land Victims'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=194&genre=0', 'Girls Got Cream'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=196&genre=0', 'Hardcore Youth'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=198&genre=0', 'Little Hellcat'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=294&genre=0', 'Little Teen Suckers'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=200&genre=0', 'Make Teen Gape'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=296&genre=0', 'Make Teen Moan'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=298&genre=0', 'MegaPenetrations'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=300&genre=0', 'Messy Gangbangs'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=302&genre=0', 'My Black Coeds'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=304&genre=0', 'My Latina Teen'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=306&genre=0', 'Nasty Ass Lickers'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=308&genre=0', 'Naughty Little Nymphs'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=310&genre=0', 'Never Done That Before'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=202&genre=0', 'Nylon Sweeties'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=312&genre=0', 'Pink Eye Sluts'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=314&genre=0', 'Plug2Holes'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=314&genre=0', 'Plug2Holes'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=316&genre=0', 'Road Gangbangs'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=318&genre=0', 'SchoolBus Chicks'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=204&genre=0', 'Seductive18'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=320&genre=0', 'Show Me Gape'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=322&genre=0', 'Shy Teachers Pet'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=324&genre=0', 'Small Tits Hunter'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=366&genre=0', 'Spermantino'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=368&genre=0', 'Teach My Ass'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=206&genre=0', 'Teen Anal Casting'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=208&genre=0', 'Teen Drillers'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=210&genre=0', 'Teen Gina'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=326&genre=0', 'Teenagers Going Wild'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=328&genre=0', 'Teens Love Blacks'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=212&genre=0', 'Teens Natural Way'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=330&genre=0', 'Teens Try Anal'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=214&genre=0', 'Teens Try Black'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=332&genre=0', 'Teens Want Orgies'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=334&genre=0', 'Tugjob Queens'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=216&genre=0', 'Try Teens'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=334&genre=0', 'White Box Black Cocks'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=336&genre=0', 'White Teens Black Cocks'],
        ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=220&genre=0', 'Young Throats'],
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': 'updates\\/(.*)\\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': link[1], 'site': link[2]},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0
        scenes = self.parse_scenepage(response)
        if scenes:
            count = len(scenes)
            for scene in scenes:
                yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def parse_scenepage(self, response):
        itemlist = []
        meta = response.meta

        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            item = SceneItem()

            item['performers'] = []
            for model in jsonentry['actors']:
                model['name'] = model['name'].replace("+", "&").strip()
                if "&" in model['name']:
                    models = model['name'].split("&")
                    for star in models:
                        item['performers'].append(star.strip().title())
                else:
                    item['performers'].append(model['name'].title())

            item['title'] = jsonentry['title_en']
            if len(re.findall(r'\w+', item['title'])) == 1 and len(item['performers']):
                if len(item['performers']) > 1:
                    item['title'] = ", ".join(item['performers']) + " (" + item['title'] + ")"
                else:
                    item['title'] = item['performers'][0] + " (" + item['title'] + ")"

            item['description'] = jsonentry['description_en']
            if not item['description']:
                item['description'] = ''

            item['image'] = jsonentry['screenshots'][0]
            if isinstance(item['image'], str):
                item['image'] = "https:" + item['image']
            else:
                item['image'] = None
            item['image_blob'] = None
            item['id'] = jsonentry['id']
            item['trailer'] = ''
            item['url'] = domain + "video/" + str(jsonentry['id']) + "/" + jsonentry['slug']
            item['date'] = self.parse_date(jsonentry['publication_start'].strip()).isoformat()
            if not item['date']:
                item['date'] = self.parse_date(jsonentry['created_at'].strip()).isoformat()
            item['site'] = meta['site']
            item['parent'] = "Teen Core Club"
            item['network'] = "Teen Core Club"

            item['tags'] = []

            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        itemlist.append(item.copy())
                else:
                    itemlist.append(item.copy())

            item.clear()
        return itemlist
