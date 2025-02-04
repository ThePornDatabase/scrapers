import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieElegantAngelSpider(BaseSceneScraper):
    name = 'MovieElegantAngel'
    network = 'Elegant Angel'
    parent = 'Elegant Angel'

    start_urls = [
        'https://www.elegantangel.com'
    ]

    cookies = [{"name": "ageConfirmed", "value": True}]

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 4,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
    }

    selector_map = {
        'title': '//h1/text()',
        'description': '///span[@class="full"]/p/text()',
        'image': 'picture img.thumbnail::attr(data-src)',
        'performers': '//div[@class="actress"]/a/text()',
        'date': '//span[@class="publish_date"]/text()',
        'tags': '',
        'external_id': 'scene/(\\d+)',
        'trailer': '',
        'pagination': '/streaming-elegant-angel-dvds-on-video.html?page=%s&hybridview=member'
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

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[@class="grid-item"]/a/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//h2[contains(text(), "Scene List")]/../following-sibling::div[contains(@class, "item-grid-scene")]/div[@class="grid-item"]/article[1]/div[1]/a/@href').getall()
        if len(scenes) > 1:
            item = SceneItem()
            item['title'] = self.cleanup_title(response.xpath('//h1[@class="description"]/text()').get().strip())
            scenedate = response.xpath('//span[contains(text(), "Released:")]/following-sibling::text()').get()
            item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).isoformat()
            description = response.xpath('//div[@class="synopsis"]/p//text()')
            if description:
                item['description'] = " ".join(description.getall())
            else:
                item['description'] = ""

            image = response.xpath('//meta[@property="og:image"]/@content|//link[@rel="image_src"]/@href')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            director = response.xpath('//a[@data-label="Director"]/text()')
            if director:
                director = director.get()
                if ":" in director:
                    director = re.search(r'\:\s+?(.*)', director).group(1).strip()
            if director:
                item['director'] = self.cleanup_title(director)
            else:
                item['director'] = ''

            item['performers'] = response.xpath('//div[@class="video-performer"]/a/span/span/text()').getall()
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))

            duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
            if duration:
                duration = duration.get().lower()
                duration = re.sub('[^0-9a-z]', '', duration)
                hours = ''
                minutes = ''
                if "hr" in duration:
                    hours = (int(re.search(r'(\d{1,2})hr', duration).group(1)) * 3600)
                else:
                    hours = 0
                if "min" in duration:
                    minutes = re.search(r'(\d{1,2})min', duration)
                    if minutes:
                        minutes = minutes.group(1)
                    else:
                        minutes = 0
                if minutes:
                    minutes = int(minutes) * 60
                else:
                    minutes = 0

                item['duration'] = str(hours + minutes)
            else:
                item['duration'] = None

            tags = response.xpath('//div[@class="categories"]//a/text()')
            if tags:
                item['tags'] = tags.getall()
            else:
                item['tags'] = []

            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Elegant Angel'
            item['parent'] = 'Elegant Angel'
            item['site'] = 'Elegant Angel'
            item['url'] = response.url
            item['id'] = re.search(r'/(\d+)/.*?\.htm', response.url).group(1)
            sceneurls = scenes
            item['scenes'] = []
            for sceneurl in sceneurls:
                if sceneurl.strip():
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'/(\d+)/.*?\.html', sceneurl).group(1)})
            meta['movie'] = item

            yield self.check_item(item, self.days)
            for sceneurl in sceneurls:
                yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()

        item['title'] = self.cleanup_title(response.xpath('//h1[@class="description"]/text()').get().strip())
        if re.search(r'(Scene \d+)', item['title']):
            if len(re.sub(r'Scene \d+', '', item['title'])) < len(movie['title']):
                item['title'] = f"{movie['title']} - {item['title']}"
        scenedate = response.xpath('//span[contains(text(), "Released:")]/following-sibling::text()').get()
        item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).isoformat()
        description = response.xpath('//div[@class="synopsis"]/p//text()')
        if description:
            item['description'] = " ".join(description.getall())
        else:
            item['description'] = ""

        image = response.xpath('//meta[@property="og:image"]/@content|//link[@rel="image_src"]/@href')
        if image:
            item['image'] = image.get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ""
            item['image_blob'] = ""

        director = response.xpath('//div[@class="director"]/text()')
        if director:
            director = director.get()
            if ":" in director:
                director = re.search(r'\:\s+?(.*)', director).group(1).strip()
        if director:
            item['director'] = self.cleanup_title(director)
        else:
            item['director'] = ''

        item['performers'] = response.xpath('//div[@class="video-performer"]/a/span/span/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))

        duration = response.xpath('//span[contains(text(), "Length:")]/following-sibling::text()')
        if duration:
            duration = duration.get().lower()
            duration = re.sub('[^0-9a-z]', '', duration)
            hours = ''
            minutes = ''
            if "hr" in duration:
                hours = (int(re.search(r'(\d{1,2})hr', duration).group(1)) * 3600)
            else:
                hours = 0
            if "min" in duration:
                minutes = re.search(r'(\d{1,2})min', duration)
                if minutes:
                    minutes = minutes.group(1)
                else:
                    minutes = 0
            if minutes:
                minutes = int(minutes) * 60
            else:
                minutes = 0

            item['duration'] = str(hours + minutes)
        else:
            item['duration'] = None

        tags = response.xpath('//div[@class="tags"]//a/text()')
        if tags:
            item['tags'] = tags.getall()
        else:
            item['tags'] = []

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]
        item['trailer'] = ''
        item['type'] = 'Scene'
        item['network'] = 'Elegant Angel'
        item['parent'] = 'Elegant Angel'
        item['site'] = 'Elegant Angel'

        item['url'] = response.url
        item['id'] = re.search(r'/(\d+)/.*?\.htm', response.url).group(1)
        yield item
