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


class SiteVurigVlaanderenSpider(BaseSceneScraper):
    name = 'VurigVlaanderen'
    network = 'Vurig Vlaanderen'
    parent = 'Vurig Vlaanderen'
    site = 'Vurig Vlaanderen'

    base_url = 'https://vurigvlaanderen.be'

    cookies = {"name": "agecookies", "value": "true"}

    headers_json = {
        'origin': 'https://vurigvlaanderen.be',
        'referer': 'https://vurigvlaanderen.be/',
        'Credentials': 'Syserauth 3-585d92b35321e910bc1c25b734531c9adf52e2679c0d42aefad09e2556cde47f-65be7945',
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
        url = 'https://api.sysero.nl/videos?page={}&count=20&type=video&include=images:types(thumb|thumb_mobile),products,categories,clips&filter[status]=published&filter[products]=1%2C2&filter[recurring]=1&sort[recommended_at]=DESC&frontend=3'
        return self.format_url(base, url.format(page))

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://vurigvlaanderen.be/sexfilms"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        link = self.get_next_page_url(self.base_url, meta['page'])
        yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers_json)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers_json)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        data = jsondata['data']
        for jsonentry in data:
            if jsonentry['attributes']['slug']:
                scene_url = "https://vurigvlaanderen.be/sexfilms/" + jsonentry['attributes']['slug']
                yield scrapy.Request(url=self.format_link(response, scene_url), callback=self.parse_scene)

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
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
                return self.parse_date(date, date_formats=['%Y-%m-%d', '%m/%d/%Y']).strftime('%Y-%m-%d')
            return self.parse_date('today').strftime('%Y-%m-%d')
        return None

    def get_duration(self, response):
        duration = response.xpath('//span[@class="time"]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration).group(1)
            return str(int(duration) * 60)
        return None

    def parse_scene(self, response):
        item = SceneItem()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)

        if not item['image']:
            item['image'] = ''
            item['image_blob'] = ''
        else:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)

        item['url'] = self.get_url(response)

        item['duration'] = self.get_duration(response)

        item['site'] = self.site
        item['network'] = self.network
        item['parent'] = self.parent

        if item['title'] and item['id']:
            yield self.check_item(item, self.days)
