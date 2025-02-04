import re
import string
import scrapy
import unidecode
import html
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieCombatZoneSpider(BaseSceneScraper):
    name = 'MovieCombatZone'
    network = 'Combat Zone'

    start_urls = [
        'https://tour.blackmarketxxx.com',
        'https://tour.fillyfilms.com',
        'https://tour.smashpictures.com',
        'https://tour.combatzonexxx.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '///span[@class="full"]/p/text()',
        'image': 'picture img.thumbnail::attr(data-src)',
        'performers': '//div[@class="actress"]/a/text()',
        'date': '//span[@class="publish_date"]/text()',
        'tags': '',
        'external_id': 'scene/(\\d+)',
        'trailer': '',
        'pagination': '/dvds/dvds_page_%s.html?s=d'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'CONCURRENT_REQUESTS_PER_IP': 2,
        "MEDIA_ALLOW_REDIRECTS": True,
    }

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

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] < 25:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[contains(@class, "item-portrait")]')
        for movie in movies:
            scenedate = movie.xpath('./div[@class="timeDate"]/text()')
            meta['date'] = ''
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')

            movie_url = self.format_link(response, movie.xpath('./div[@class="modelPic"]/a/@href').get())
            if "/dvds/dvds.html" not in movie_url:
                yield scrapy.Request(movie_url, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        sceneurls = response.xpath('//div[contains(@class, "item-thumb")]/a/@href').getall()
        sceneurls = list(filter(lambda x: len(x) > 0, sceneurls))
        if len(sceneurls) > 1:
            item = SceneItem()
            item['network'] = 'Combat Zone'
            item['site'] = response.xpath('//div[contains(@class,"bioDetails")]//p[contains(text(), "Studio")]/b[1]/text()|//div[contains(@class,"bioDetails")]//text()[contains(., "Studio")]/following-sibling::b[1]/text()').get()
            item['parent'] = item['site']
            item['url'] = response.url
            item['id'] = re.search(r'/(dvds/.*?)\.htm', response.url).group(1)
            item['id'] = item['id'].lower().replace("/", "-")

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//h2/i[contains(@class, "fa-film")]/following-sibling::text()').get()).strip()))
            item['date'] = meta['date']

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:
                item['description'] = ""

                image = response.xpath('//div[contains(@class,"bioPic")]/img/@src0_3x|//div[contains(@class,"bioPic")]/img/@src0_2x|//div[contains(@class,"bioPic")]/img/@src0_1x')
                item['image'] = ''
                item['image_blob'] = ''
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                performers = response.xpath('//div[contains(@class,"bioDetails")]//p[contains(text(), "Studio")]/b[1]/following-sibling::text()[contains(., "Starring:")]|//div[contains(@class,"bioDetails")]//p//text()[contains(., "Starring")]')
                if performers:
                    performers = performers.get()
                    performers = performers.lower()
                    performers = performers.replace("starring:", "")
                    performers = performers.split(",")
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))

                duration = response.xpath('//div[contains(@class, "item-video")]//div[@class="timeDate"]/text()[1]').getall()
                tot_minutes = 0
                tot_seconds = 0
                for dur_entry in duration:
                    if ":" in dur_entry:
                        dur_entry = re.search(r'(\d+):(\d+)', dur_entry)
                        if dur_entry:
                            minutes = 0
                            seconds = 0
                            minutes = dur_entry.group(1)
                            tot_minutes = tot_minutes + (int(minutes) * 60)
                            seconds = dur_entry.group(2)
                            tot_seconds = tot_seconds + int(seconds)
                item['duration'] = str(tot_minutes + tot_seconds)

                director = response.xpath('//div[contains(@class,"bioDetails")]//p[contains(text(), "Studio")]/b[1]/following-sibling::text()[contains(., "Director:")]|//div[contains(@class,"bioDetails")]//p//text()[contains(., "Director")]')
                if director:
                    item['director'] = re.search(r':(.*)', director.get()).group(1)
                    item['director'] = string.capwords(item['director'].replace("\r", "").replace("\n", "").replace("\t", "").strip())

                tags = []
                tags = response.xpath('//div[contains(@class,"bioDetails")]//p[contains(text(), "Studio")]/b[1]/following-sibling::text()[contains(., "Categories:")]|//div[contains(@class,"bioDetails")]//p//text()[contains(., "Categories")]')
                if tags:
                    tags = tags.get()
                    tags = tags.lower()
                    tags = tags.replace("categories:", "")
                    tags = tags.split(",")
                    item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []
                for sceneurl in sceneurls:
                    sceneid = re.search(r'/(trailers/.*?)\.htm', sceneurl).group(1)
                    item['scenes'].append({'site': item['site'], 'external_id': sceneid.lower().replace("/", "-")})

                meta['scenelist'] = response.xpath('//div[contains(@class,"item-grid-scene")]//article/div[1]')

                meta['movie'] = item.copy()

                if self.check_item(item, self.days):
                    for sceneurl in sceneurls:
                        yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
                    yield item

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        item['network'] = 'Combat Zone'
        item['parent'] = movie['site']
        item['site'] = movie['site']
        item['url'] = response.url
        sceneid = re.search(r'/(trailers/.*?)\.htm', response.url).group(1)
        item['id'] = sceneid.lower().replace("/", "-")

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]

        item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//h2/i[contains(@class, "fa-film")]/following-sibling::text()').get()).strip()))
        shorttitle = re.sub(r'scene \d+', '', item['title'].lower())
        shorttitle = shorttitle.replace("\r", "").replace("\n", "").replace("\t", "").strip()
        if len(shorttitle) < 5:
            item['title'] = f"{movie['title']} - {item['title']}"

        scenedate = response.xpath('//div[@class="info"]//p/text()[contains(., "Added:")]')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
        else:
            item['date'] = ''

        description = response.xpath('//div[@class="description"]/p/text()')
        if description:
            item['description'] = self.cleanup_description(description.get())
        else:
            item['description'] = ''

        image = response.xpath('//img[contains(@class, "update_thumb")]/@src0_3x|//img[contains(@class, "update_thumb")]/@src0_2x|//img[contains(@class, "update_thumb")]/@src0_1x')
        if image:
            item['image'] = self.format_link(response, image.get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['performers'] = response.xpath('//div[@class="info"]//p/text()[contains(., "Featuring:")]/following-sibling::a/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))

        director = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="director"]/a/text()')
        if director:
            item['director'] = director.get()
            item['director'] = item['director'].replace("\r", "").replace("\n", "").replace("\t", "").strip()

        duration = response.xpath('//div[@class="info"]//p/text()[contains(., "Runtime:")]')
        item['duration'] = None
        if duration:
            duration = re.search(r'(\d+):(\d+)', duration.get())
            if duration:
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                item['duration'] = str(minutes + seconds)

        tags = response.xpath('//ul[contains(@class, "tags")]/li/a/text()')
        if tags:
            item['tags'] = tags.getall()
        else:
            item['tags'] = []

        item['trailer'] = ''
        item['type'] = "Scene"

        yield item
