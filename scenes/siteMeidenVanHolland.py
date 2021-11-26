import re
from datetime import date, timedelta
import codecs
import json
import scrapy
from tpdb.items import SceneItem

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_tag(argument):
    match = {
        'debutanten': "First Time",
        'anaal': "Anal",
        'dikke tieten': "Big Boobs",
        'amateur sex': "Amateur",
        'volle vrouw': "BBW",
        'duo': "FM",
        'gangbang': "Gangbang",
        'trio': "Threesome",
        'jonge meid': "18+ Teens",
        'squirten': "Squirting",
        'pov': "POV",
        'lesbisch': "Lesbian",
        'pijpen': "Blowjob",
        'buitensex': "Outdoors",
        'bdsm': "BDSM",
        'rollenspel': "Roleplay",
        'internationaal': "International",
        'klassiekers': "Classics",
        'milf': "MILF",
    }
    return match.get(argument, '')


class SiteMedienVanHolldandSpider(BaseSceneScraper):
    name = 'MeidenVanHolland'
    network = 'Meiden Van Holland'
    parent = 'Meiden Van Holland'
    site = 'Meiden Van Holland'

    base_url = 'https://meidenvanholland.nl'

    headers_json = {
        'accept': 'application/json, text/plain, */*',
        'credentials': 'Syserauth 1-5d73b3eb1647d9e91a9d7280777c4aef'
                       'e4d25efa1367f5bc5bd03121415038ac-6128070c',
        'origin': 'https://meidenvanholland.nl',
        'referer': 'https://meidenvanholland.nl',
    }

    selector_map = {
        'title': '//script[contains(text(),"NUXT")]/text()',
        're_title': r'video:\{title:\"(.*?)\"',
        'description': '//script[contains(text(),"NUXT")]/text()',
        're_description': r'description:\"(.*?)\"',
        'date': '//script[contains(text(),"NUXT")]/text()',
        're_date': r'pivot_data:\{active_from:\"(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@name="og:image"]/@content',
        'performers': '//script[contains(text(),"NUXT")]/text()',
        're_performers': r'models:\[(.*?)\]',
        'tags': '//script[contains(text(),"NUXT")]/text()',
        'external_id': r'sexfilms\/(.*)',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def get_next_page_url(self, base, page):
        url = 'https://api.sysero.nl/videos?page={}&count=20&include=images' \
            ':types(thumb):limit(1|0),products,categories&filter' \
            '[status]=published&filter[products]=1%2C2&filter[types]' \
            '=video&sort[recommended_at]=DESC&frontend=1'
        return self.format_url(base, url.format(page))

    def start_requests(self):
        yield scrapy.Request(url=self.get_next_page_url(
                             self.base_url, self.page),
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers_json,
                             cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene
        if count:
            if 'page' in response.meta \
                    and response.meta['page'] < self.limit_pages:
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
        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            if jsonentry['attributes']['slug']:
                scene_url = "https://meidenvanholland.nl/sexfilms/" \
                            + jsonentry['attributes']['slug']
                yield scrapy.Request(url=self.format_link(response, scene_url),
                                     callback=self.parse_scene)

    def get_performers(self, response):
        performers = self.process_xpath(response,
                                        self.get_selector_map('performers'))
        if performers:
            performers = performers.get()
            performers = re.search(
                r',models:\[(.*id:\".*?)\],preroll',
                performers)
            if performers:
                performers = performers.group(1)
                performers = re.findall('title:\"(.*?)\"', performers)
                return list(map(lambda x: x.strip(), performers))
        return []

    def get_tags(self, response):
        tags = self.process_xpath(response, self.get_selector_map('tags'))
        if tags:
            tags = tags.get()
            tags = re.search(r',categories:\[(.*?)\],products', tags)
            if tags:
                tags = tags.group(1)
                tags = re.findall(r'name:\"(.*?)\"', tags)
                tags2 = ['European']
                for tag in tags:
                    found_tag = match_tag(tag.lower())
                    if found_tag:
                        tags2.append(found_tag)
                return list(map(lambda x: x.strip().title(), tags2))
        return []

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''

        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = self.get_from_regex(description.get(), 're_description')

            if description:
                try:
                    description = codecs.decode(description, 'unicode-escape')
                except Exception:
                    description = re.sub(r'\\u00\d[a-fA-F]', '', description)
                description = re.sub(r'<[^<]+?>', '', description).strip()
                description = re.sub(
                    r'[^a-zA-Z0-9\-_ \.\?\!]', '', description)
                return self.cleanup_description(description)
        return ''

    def get_date(self, response):
        datestring = self.process_xpath(response, self.get_selector_map('date'))
        if datestring:
            datestring = datestring.get().replace(r"\u002F", "/")
            date = re.search(self.get_selector_map('re_date'), datestring)
            if not date:
                date = re.search(r'active_from=\"(\d{4}-\d{2}-\d{2})', datestring)
            if not date:
                date = re.search(r'active_from:\"(\d{1,2}/\d{1,2}/\d{2})', datestring)
            if date:
                date = date.group(1)
                return self.parse_date(date, date_formats=['%Y-%m-%d', '%m/%d/%Y']).isoformat()
            return self.parse_date('today').isoformat()
        return None

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if not item['image']:
            item['image'] = None

        item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        else:
            item['parent'] = self.get_parent(response)

        if item['title'] and item['id']:
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
                        yield item
                else:
                    yield item
