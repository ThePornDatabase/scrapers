import re
import string
import scrapy
import unidecode
import html
from tpdb.helpers.dbhelper import db_conn
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieNewSensationsSpider(BaseSceneScraper):
    name = 'MovieNewSensations'
    network = 'New Sensations'

    start_urls = [
        'https://www.newsensations.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '///span[@class="full"]/p/text()',
        'image': 'picture img.thumbnail::attr(data-src)',
        'performers': '//div[@class="actress"]/a/text()',
        'date': '//span[@class="publish_date"]/text()',
        'tags': '',
        'external_id': r'.*/(.*?)\.htm',
        'trailer': '',
        'pagination': '/tour_ns/dvds/dvds_page_%s.html?s=d'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        # ~ 'AUTOTHROTTLE_ENABLED': True,
        # ~ 'CONCURRENT_REQUESTS': 2,
        # ~ 'USE_PROXY': True,
        # ~ 'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        # ~ 'CONCURRENT_REQUESTS_PER_IP': 2,
        # ~ "MEDIA_ALLOW_REDIRECTS": True,
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
        movies = response.xpath('//div[contains(@class,"modelBlock")]')
        for movie in movies:
            meta['image'] = movie.xpath('./a//img/@src0_2x').get()

            movie = movie.xpath('./a[1]/@href').get()
            if "/dvds/" in movie:
                yield scrapy.Request(movie, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="dvdScene"]')
        if len(scenes) > 1:
            item = self.init_scene()
            item['network'] = "New Sensations"
            item['site'] = "New Sensations"
            item['parent'] = item['site']
            item['url'] = response.url
            item['id'] = response.xpath('//div[contains(@class,"sceneRating")]//comment()[contains(., "data-id")]').get()
            item['id'] = re.search(r'data-id="(\d+)"', item['id']).group(1)

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//div[@class="indSceneDVD"]/h1/text()').get()).strip()))
            item['date'] = response.xpath('//div[@class="datePhotos"]/span/text()').get()
            if re.search(r'(\d{4}-\d{2}-\d{2})', item['date']):
                item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', item['date']).group(1)
            elif re.search(r'(\d{2}-\d{2}-\d{4})', item['date']):
                item['date'] = re.search(r'(\d{2}-\d{2}-\d{4})', item['date']).group(1)
                item['date'] = self.parse_date(item['date'], date_formats=['%m-%d-%Y']).strftime('%Y-%m-%d')

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:
                description = response.xpath('//div[@class="description"]//h2/text()[1]')
                if description:
                    item['description'] = self.cleanup_description(description.get())

                if meta['image']:
                    image = meta['image'].strip()
                else:
                    image = ''
                item['image'] = ''
                item['image_blob'] = ''
                if image:
                    item['image'] = image
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                performers = response.xpath('//span[@class="tour_update_models"]/a/text()')
                if performers:
                    performers = performers.getall()
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))

                duration = response.xpath('//div[@class="dvdScene"]//div[@class="dvdDatePhotos"]/span/text()[contains(., "min")]').getall()
                tot_minutes = 0
                for dur_entry in duration:
                    if "min" in dur_entry:
                        dur_entry = re.sub(r'[^a-z0-9]+', '', dur_entry)
                        minutes = re.search(r'(\d+)min', dur_entry)
                        if minutes:
                            minutes = minutes.group(1)
                            tot_minutes = tot_minutes + (int(minutes) * 60)
                item['duration'] = str(tot_minutes)

                tags = []
                tags = response.xpath('//div[@class="dvdScene"]//div[contains(@class, "dvdCate")]//a/text()')
                if tags:
                    tags = tags.getall()
                    tags = list(map(lambda x: string.capwords(x.strip()), tags))
                    item['tags'] = list(set(tags))

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []
                for scene in scenes:
                    sceneurl = scene.xpath('./h2/a/@href').get()
                    sceneid = scene.xpath('.//comment()[contains(., "data-id")]').get()
                    sceneid = re.search(r'data-id.*?(\d+)', sceneid).group(1)
                    site = self.lookup_scene(sceneid)
                    if not site:
                        site = "New Sensations"
                    item['scenes'].append({'site': site, 'external_id': sceneid.lower()})

                meta['movie'] = item.copy()

                if self.check_item(item, self.days):
                    for scene in scenes:
                        sceneurl = scene.xpath('./h2/a/@href').get()
                        scenetags = scene.xpath('.//div[contains(@class,"dvdCate")]//a/text()')
                        if scenetags:
                            meta['scenetags'] = scenetags.getall()
                        else:
                            meta['scenetags'] = []
                        yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
                    yield item

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = self.init_scene()
        item['network'] = 'New Sensations'
        item['parent'] = 'New Sensations'

        item['url'] = response.url
        item['id'] = self.get_id(response)

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]

        item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//div[@class="indScene"]/h1/text()').get()).strip()))
        shorttitle = re.sub(r'scene \d+', '', item['title'].lower())
        shorttitle = shorttitle.replace("\r", "").replace("\n", "").replace("\t", "").strip()
        if len(shorttitle) < 5:
            item['title'] = f"{movie['title']} - {item['title']}"

        scenedate = response.xpath('//div[@class="sceneDateP"]/span/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
        else:
            item['date'] = ''

        description = response.xpath('//div[@class="description"]//h2/text()')
        if description:
            item['description'] = self.cleanup_description(description.get())
        else:
            item['description'] = ''

        image = response.xpath('//div[contains(@class,"indvideo")]/span/a/span[1]/img[1]/@src')
        if image:
            item['image'] = image.get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'].strip())
        else:
            item['image'] = ''
            item['image_blob'] = ''

        item['performers'] = response.xpath('//div[@class="indScene"]//span[@class="tour_update_models"]/a/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))

        duration = response.xpath('//div[@class="sceneDateP"]/text()')
        if duration:
            duration = duration.get()
            if "min" in duration:
                duration = re.sub(r'[^a-z0-9]+', '', duration)
                minutes = re.search(r'(\d+)min', duration)
                if minutes:
                    minutes = minutes.group(1)
                    item['duration'] = str(int(minutes) * 60)

        item['tags'] = meta['scenetags']

        item['trailer'] = ''
        item['type'] = "Scene"
        site = self.lookup_scene(item['id'])
        if site:
            item['site'] = site
            item['force_update'] = True
            item['force_fields'] = 'tags,movies'
        else:
            item['site'] = "New Sensations"

        yield item

    def lookup_scene(self, sceneid):

        #######################################################
        # Check to see if the movie has already been submitted.  If so, no reason to pull the images or scenes
        conn, cursor = db_conn()

        cursor.execute("SELECT scene_site FROM nscache WHERE scene_id = %s", (sceneid,))
        if cursor.rowcount:
            scene_site = cursor.fetchone()[0]
            return scene_site

        cursor.close()
        conn.close()
        return False

    def get_id(self, response):
        sceneid = response.xpath('//comment()[contains(.,"data-id")]')
        if sceneid:
            return re.search(r'data-id=\"(\d+)\"', sceneid.get()).group(1)
        return None
