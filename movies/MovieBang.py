import re
import html
import json
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieBangSpider(BaseSceneScraper):
    name = 'MovieBang'
    network = 'Bang'
    parent = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '//div[contains(@class, "actions")]/a[contains(@href, "with")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = f"https://www.bang.com/movies?by=date.desc&page={page}"
        # ~ pagination = f"https://www.bang.com/studio/157/video-art-holland/movies?by=date.desc&page={page}"
        # ~ pagination = f"https://www.bang.com/studio/239/melting-images/movies?by=trending&page={page}"
        # ~ pagination = f"https://www.bang.com/videos?by=date.desc&in=BANG%21%20Real%20Teens&page={page}"
        # ~ pagination = f"https://www.bang.com/videos?in=BANG!%20Surprise&page={page}"
        return pagination

    def parse(self, response, **kwargs):
        meta = response.meta
        movies = self.get_movies(response)
        count = 0
        for movie in movies:
            count += 1
            meta['movie'] = movie
            yield movie
            # ~ for sceneurl in movie['sceneurls']:
                # ~ yield scrapy.Request(self.format_link(response, sceneurl), meta=meta, callback=self.parse_scene, headers=self.headers, cookies=self.cookies)

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[contains(@class,"movie-preview")]/a/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scene_count = response.xpath('//div[@class="scene-section" and not(contains(./div/h2/text(), "Bonus"))]')
        if len(scene_count) > 1:
            item = SceneItem()
            jsondata = response.xpath('//script[contains(@type, "json") and contains(text(), "duration")]/text()')
            if jsondata:
                jsondata = json.loads(jsondata.get(), strict=False)
                item['title'] = self.cleanup_title(unidecode.unidecode(jsondata['name'])).replace("&", "and")
                item['date'] = jsondata['datePublished']
                if 'description' in jsondata:
                    item['description'] = html.unescape(jsondata['description'])
                else:
                    item['description'] = ''
                item['image'] = jsondata['thumbnailUrl']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = response.xpath('//a[contains(@href, "related-movie")]/@href').get()
                item['id'] = re.search(r'movie=(.*)$', item['id']).group(1)
                item['type'] = 'Movie'
                item['url'] = response.url
                item['duration'] = self.duration_to_seconds(jsondata['duration'])
                item['performers'] = []
                for person in jsondata['actor']:
                    item['performers'].append(person['name'])

                item['tags'] = response.xpath('//div[@class="relative"]/div/a[@class="genres"]/text()').getall()

                item['site'] = re.sub('[^a-zA-Z0-9-]', '', response.xpath('//p[contains(text(), "Studio:")]/a/text()').get())
                item['trailer'] = ""
                item['store'] = 'Bang'
                item['network'] = item['site']
                item['parent'] = item['site']

                # ~ sceneurls = response.xpath('//div[@class="scene-section"]/div/div/a[contains(@href, "/video/")][1]/@href').getall()
                item['scenes'] = []
                scenes = response.xpath('//div[@class="scene-section"]')
                sceneurls = []
                for scene in scenes:
                    sceneurls.append(scene.xpath('.//h2/following-sibling::div[1]/a[1]/@href').get())
                    sceneid = scene.xpath('.//div[contains(@class, "hidden") and contains(@class, "px-4")]/a[1]/@href').get()
                    if "related-video" in sceneid:
                        sceneid = re.search(r'related-video=(\w+)', sceneid).group(1)
                    item['scenes'].append({'site': item['site'], 'external_id': sceneid})
                meta['movie'] = item.copy()
                # ~ matches = ['private', 'bluebird', 'lethalhardcore', 'thagson', 'samurai', 'premiumx', 'littledragon', 'karups', 'joybear', 'heatwave', 'fillyfilms', 'baeb']
                matches = ['private', 'lethalhardcore', 'thagson', 'samurai', 'premiumx', 'littledragon', 'karups', 'joybear', 'heatwave', 'fillyfilms', 'baeb', 'zerotolerance', 'zerotolerancefilms', 'zerotoleranceent', 'burningangel', 'burningangelentertainment']
                if not any(x in re.sub('[^a-zA-Z0-9]', '', item['site']).lower() for x in matches):
                    if item['id']:
                        yield self.check_item(item, self.days)
                        # ~ if self.check_item(item, self.days):
                            # ~ for sceneurl in sceneurls:
                                # ~ yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()
        jsondata = response.xpath('//script[contains(@type, "json") and contains(text(), "duration")]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get(), strict=False)
            item['title'] = self.cleanup_title(jsondata['name'])
            item['date'] = jsondata['datePublished']
            if 'description' in jsondata:
                item['description'] = html.unescape(jsondata['description'])
            else:
                item['description'] = ''
            item['image'] = jsondata['thumbnailUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = jsondata['@id']
            item['type'] = 'Scene'
            item['url'] = response.url
            item['duration'] = self.duration_to_seconds(jsondata['duration'])
            item['performers'] = []
            for person in jsondata['actor']:
                item['performers'].append(person['name'])

            item['tags'] = self.get_tags(response)
            site = jsondata['productionCompany']['name']
            item['site'] = re.sub('[^a-zA-Z0-9-]', '', site)
            trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "mp4")]/@src')
            if not trailer:
                trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "webm")]/@src')
            if trailer:
                item['trailer'] = trailer.get()
            else:
                item['trailer'] = ''
            item['movies'] = [{'site': meta['movie']['site'], 'external_id': meta['movie']['id']}]
            item['network'] = 'Bang'
            item['parent'] = 'Bang'

            yield self.check_item(item, self.days)
