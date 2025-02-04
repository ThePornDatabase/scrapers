import re
import string
import scrapy
import unidecode
import html
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieEvasiveAnglesSpider(BaseSceneScraper):
    name = 'MovieEvasiveAngles'

    start_urls = [
        'https://www.evasiveangles.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '///span[@class="full"]/p/text()',
        'image': 'picture img.thumbnail::attr(data-src)',
        'performers': '//div[@class="actress"]/a/text()',
        'date': '//span[@class="publish_date"]/text()',
        'tags': '',
        'external_id': '/(\d+)/',
        'trailer': '',
        'pagination': '/evasive-angles-new-release-porn-videos.html?sort=added&page=%s&studio=22235'
        # ~ 'pagination': '/evasive-angles-new-release-porn-videos.html?sort=added&page=%s&studio=95400'
        # ~ 'pagination': '/evasive-angles-new-release-porn-videos.html?sort=added&page=%s&studio=95399'
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
        movies = response.xpath('//div[@class="grid-item"]/a[1]/@href').getall()
        for movie in movies:
            movie_url = self.format_link(response, movie)
            yield scrapy.Request(movie_url, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        sceneurls = response.xpath('//h2[contains(text(), "Scene List")]/../following-sibling::div//article/div[1]/a[1]/@href').getall()
        sceneurls = list(filter(lambda x: len(x) > 0, sceneurls))
        if len(sceneurls) > 1:
            item = SceneItem()
            item['network'] = 'Evasive Angles'
            item['parent'] = 'Evasive Angles'
            item['site'] = 'Evasive Angles'
            # ~ item['parent'] = 'T.T. Boy Productions'
            # ~ item['site'] = 'T.T. Boy Productions'
            # ~ item['parent'] = 'Love\'s Kitty Films'
            # ~ item['site'] = 'Love\'s Kitty Films'
            item['url'] = response.url
            item['id'] = re.search(r'/(\d+)/', response.url).group(1)

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//h1[@class="description"]/text()').get()).strip()))

            scenedate = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()').get()
            if scenedate:
                item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            else:
                item['date'] = ''

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:
                description = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="synopsis"]//text()').getall()
                description = "".join(description)
                item['description'] = self.cleanup_description(description)

                image = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="modal-body"]/div[1]/div[1]/div[1]/img/@data-src')
                item['image'] = ''
                item['image_blob'] = ''
                if image:
                    item['image'] = image.get()
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['performers'] = response.xpath('//p[@class="scene-performer-names"]/a/text()').getall()
                item['performers'] = list(map(lambda x: "".join(x).strip(), item['performers']))

                duration = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="release-date"]/span[contains(text(), "Length")]/following-sibling::text()')
                if duration:
                    duration = duration.get().lower().replace(" ", "")
                    hours = ''
                    minutes = ''
                    if "hrs" in duration:
                        hours = (int(re.search(r'(\d{1,2})hrs', duration).group(1)) * 3600)
                    else:
                        hours = 0
                    if "min" in duration:
                        minutes = (int(re.search(r'(\d{1,2})min', duration).group(1)) * 60)
                    else:
                        minutes = 0
                    item['duration'] = str(hours + minutes)
                else:
                    item['duration'] = None

                director = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="director"]/a/text()')
                if director:
                    item['director'] = director.get()
                    item['director'] = item['director'].replace("\r", "").replace("\n", "").replace("\t", "").strip()

                tags = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="categories"]/a/text()')
                if tags:
                    item['tags'] = tags.getall()
                else:
                    item['tags'] = []

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []
                for sceneurl in sceneurls:
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'/(\d+)/', sceneurl).group(1)})

                meta['scenelist'] = response.xpath('//div[contains(@class,"item-grid-scene")]//article/div[1]')

                meta['movie'] = item.copy()

                if self.check_item(item, self.days):
                    for sceneurl in sceneurls:
                        yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
                    yield item

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        scenelist = meta['scenelist']
        item = SceneItem()
        item['network'] = 'Evasive Angles'
        item['parent'] = 'Evasive Angles'
        item['site'] = 'Evasive Angles'
        # ~ item['parent'] = 'T.T. Boy Productions'
        # ~ item['site'] = 'T.T. Boy Productions'
        # ~ item['parent'] = 'Love\'s Kitty Films'
        # ~ item['site'] = 'Love\'s Kitty Films'
        item['url'] = response.url
        item['id'] = re.search(r'/(\d+)/', response.url).group(1)

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]

        item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//h1[@class="description"]/text()').get()).strip()))

        shorttitle = re.sub(r'scene \d+', '', item['title'].lower())
        shorttitle = shorttitle.replace("\r", "").replace("\n", "").replace("\t", "").strip()
        if len(shorttitle) < 5:
            item['title'] = f"{movie['title']} - {item['title']}"

        scenedate = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()').get()
        if scenedate:
            item['date'] = self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
        else:
            item['date'] = ''

        description = response.xpath('//div[contains(@class,"video-details-container")]//h5[@class="tag-line"]/text()').getall()
        description = "".join(description)
        item['description'] = self.cleanup_description(description)

        image = response.xpath('//meta[@property="og:image"]/@content')
        item['image_blob'] = ''
        item['image'] = ''
        if image:
            item['image'] = image.get()

        for sceneitem in scenelist:
            sceneitem_url = sceneitem.xpath('./a/@href').get()
            if sceneitem_url in response.url:
                image = sceneitem.xpath('.//img/@data-src')
                if image:
                    item['image'] = image.get()

        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['performers'] = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="video-performer"]/a/span/span/text()').getall()
        item['performers'] = list(map(lambda x: "".join(x).strip(), item['performers']))

        director = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="director"]/a/text()')
        if director:
            item['director'] = director.get()
            item['director'] = item['director'].replace("\r", "").replace("\n", "").replace("\t", "").strip()

        duration = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="release-date"]/span[contains(text(), "Length")]/following-sibling::text()')
        if duration:
            duration = duration.get().lower().replace(" ", "")
            hours = ''
            minutes = ''
            if "hrs" in duration:
                hours = (int(re.search(r'(\d{1,2})hrs', duration).group(1)) * 3600)
            else:
                hours = 0
            if "min" in duration:
                minutes = (int(re.search(r'(\d{1,2})min', duration).group(1)) * 60)
            else:
                minutes = 0
            item['duration'] = str(hours + minutes)
        else:
            item['duration'] = None

        tags = response.xpath('//div[contains(@class,"video-details-container")]//div[@class="categories"]/a/text()')
        if tags:
            item['tags'] = tags.getall()
        else:
            item['tags'] = []

        item['trailer'] = ''
        item['type'] = "Scene"

        yield item
