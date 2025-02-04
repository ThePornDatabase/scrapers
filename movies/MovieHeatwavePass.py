import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieHeatwaveSpider(BaseSceneScraper):
    name = 'MovieHeatwave'
    network = 'Heatwave'
    parent = 'Heatwave'
    site = 'Heatwave'

    start_urls = [
        'http://www.heatwavepass.com'
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
        'pagination': '/dvds.html?p=%s'
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
        movies = response.xpath('//ul[contains(@class,"dvd-list")]/li/a[1]/@href').getall()
        for movie in movies:
            movie_url = self.format_link(response, movie)
            yield scrapy.Request(movie_url, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        sceneurls = response.xpath('//div[contains(@class,"dvd-item")]//a[contains(text(), "Play Scene")]/@href').getall()
        sceneurls = list(filter(lambda x: len(x) > 0, sceneurls))
        if len(sceneurls) > 1:
            item = SceneItem()
            item['network'] = 'Heatwave'
            item['parent'] = 'Heatwave'
            item['site'] = 'Heatwave'
            item['url'] = response.url
            item['id'] = re.search(r'.*-(\d+)\.htm', response.url).group(1)

            item['title'] = self.cleanup_title(response.xpath('//div[contains(@class,"dvd-info")]//h1/text()').get().strip())

            scenedate = response.xpath('//div[contains(@class,"dvd-info")]//span[contains(text(), "Added")]/following-sibling::text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            else:
                item['date'] = "2012-01-01"

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:

                item['description'] = ''

                image = response.xpath('//div[contains(@id, "cover-front")]/@style')
                item['image'] = ''
                item['image_blob'] = ''
                if image:
                    image = image.get()
                    item['image'] = re.search(r'(http.*?)\)', image).group(1)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['performers'] = response.xpath('//div[contains(@class,"dvd-info")]//div[@class="stars"]//a[contains(@href, "/pornstars/")]/text()').getall()
                item['performers'] = list(map(lambda x: x.strip(), item['performers']))

                duration = response.xpath('//div[contains(@class,"dvd-info")]//span[contains(text(), "Duration")]/following-sibling::text()')
                if duration:
                    duration = duration.get().lower().replace(" ", "")
                    hours = ''
                    minutes = ''
                    if "h" in duration:
                        hours = (int(re.search(r'(\d{1,2})h', duration).group(1)) * 3600)
                    else:
                        hours = 0
                    if "m" in duration:
                        minutes = (int(re.search(r'(\d{1,2})m', duration).group(1)) * 60)
                    else:
                        minutes = 0
                    if "s" in duration:
                        seconds = int(re.search(r'(\d{1,2})s', duration).group(1))
                    else:
                        seconds = 0
                    item['duration'] = str(hours + minutes + seconds)
                else:
                    item['duration'] = None

                tags = response.xpath('//div[contains(@class,"dvd-info")]//span[contains(text(), "Tags")]/following-sibling::div[1]//a/text()')
                if tags:
                    item['tags'] = tags.getall()
                else:
                    item['tags'] = []

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []
                for sceneurl in sceneurls:
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'.*-(\d+)\.htm', sceneurl).group(1)})
                meta['movie'] = item.copy()

                if self.check_item(item, self.days):
                    for sceneurl in sceneurls:
                        yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
                    yield item

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        item['title'] = self.cleanup_title(response.xpath('//h1[@class="title"]/text()').get().strip())

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]

        scenedate = response.xpath('//div[contains(@id,"info_container")]//span[contains(text(), "Added")]/following-sibling::text()').get()
        item['date'] = "2012-01-01"
        if scenedate:
            scenedate = self.parse_date(scenedate, date_formats=['%b %d, %Y'])
            if scenedate:
                item['date'] = scenedate.strftime('%Y-%m-%d')

        description = response.xpath('//div[@id="description_container"]//text()')
        if description:
            item['description'] = self.cleanup_description(" ".join(description.getall()).strip())
        else:
            item['description'] = ''

        image = response.xpath('//div[@id="promo-shots"]/div[1]/@style')
        item['image'] = ""
        item['image_blob'] = ''
        if image:
            image = re.search(r'(http.*?)\)', image.get()).group(1)
            if "/images/" in image:
                image = image.replace("/images/", "/sc/")
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = response.xpath('//div[@class="cast"]//div[@class="name"]/a/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))

        tags = response.xpath('//span[contains(text(), "Tags")]/following-sibling::a/text()')
        if tags:
            item['tags'] = list(map(lambda x: x.strip(), tags.getall()))
        else:
            item['tags'] = []

        item['trailer'] = ''
        item['type'] = 'Scene'

        item['site'] = "Heatwave"
        item['parent'] = item['site']
        item['network'] = 'Heatwave'

        duration = response.xpath('//span[contains(text(), "Duration")]/following-sibling::text()')
        if duration:
            duration = duration.get().lower().replace(" ", "")
            hours = ''
            minutes = ''
            if "h" in duration:
                hours = (int(re.search(r'(\d{1,2})h', duration).group(1)) * 3600)
            else:
                hours = 0
            if "m" in duration:
                minutes = (int(re.search(r'(\d{1,2})m', duration).group(1)) * 60)
            else:
                minutes = 0
            if "s" in duration:
                seconds = int(re.search(r'(\d{1,2})s', duration).group(1))
            else:
                seconds = 0
            item['duration'] = str(hours + minutes + seconds)
        else:
            item['duration'] = None

        item['url'] = response.url
        item['id'] = re.search(r'.*-(\d+)\.htm', response.url).group(1)
        yield item
