import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class MovieNathanBlakeSpider(BaseSceneScraper):
    name = 'MovieNathanBlake'
    network = 'Nathan Blake'
    parent = 'Nathan Blake'

    start_urls = [
        'https://nathansluts.com'
    ]

    cookies = [{"domain":"nathansluts.com","expirationDate":1712439997,"hostOnly":true,"httpOnly":false,"name":"ns_disclaimer","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"1"},{"domain":"nathansluts.com","hostOnly":true,"httpOnly":true,"name":"_nathansluts_session2","path":"/","sameSite":"unspecified","secure":true,"session":true,"storeId":"0","value":"WXNUb01VMjJwS0hBd05pVk5pRmlWMDJCVXBha0VDeG4vSjVzQksyS0JuRXhxamZRbTZ5bHlwUVB0d3d0eTVGenJKNnN4T0p6MG1DUG1tWFd0K25lUmpDTEVrVmhqbDEzS0R0cUNwWWVOTDd4UTExOEl5VHdOaGE4aTJwOHFyZThXZUdtMGlnUkI4VXFyWkZHTmM1WVVkVzE0aVN4UjZleVdaQnZib2ROSFNvd1U2Yzl0QmlxTUNCbDFXb2xsZDFNVVRha01BNCtvb2dPTlN0Nzkzd2Uvd2pFbVRQUlZsd1hmK0JNeFpJT0JSVmdZSTNPdWpEYmR5WExMdlZSM0FBeVl6aHdkSUVzaHRGZXpUOFQxNHhTcVBjYXUyY1dFMkZidTNVQlZsSkgweDV3N1lTa3prSWh1WWNwK2loN1UwOUQtLVoxR3hIWmJtTDZBSjVWazRWcWc5c2c9PQ%3D%3D--538036a66b090009f9b4a7ee85872229b9c62e01"}]

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
        'pagination': '/get_dvds/%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://nathansluts.com"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies, dont_filter=True)

    def start_requests_2(self, response):
        meta = response.meta
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, cookies=self.cookies, meta=meta,dont_filter=True)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta,dont_filter=True)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div/a[contains(@href, "/dvds/")]/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//comment()[contains(., "Scenes")]/following-sibling::div[1]//a[contains(@href, "/videos/")]/@href').getall()
        if len(scenes) > 1:
            item = SceneItem()

            item['title'] = self.cleanup_title(response.xpath('//div[@class="nsDvdDetails"]/following-sibling::div[1]/text()').get().strip())

            scenedate = response.xpath('//div[contains(text(), "Released:")]/text()').get()
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)

            description = response.xpath('//div[@id="dvddescription"]/text()')
            if description:
                item['description'] = " ".join(description.getall())
            else:
                item['description'] = ""

            image = response.xpath('//div[@class="nsDvdDetails"]/../..//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            item['director'] = "Nathan Blake"

            item['performers'] = response.xpath('//div[contains(@id, "star") and contains(@id, "Movie")]/a/text()').getall()
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))

            duration = response.xpath('//comment()[contains(., "Scenes")]/following-sibling::div[1]//a[contains(@href, "/videos/")]//div[@class="movieTitle"]/span/text()')
            if duration:
                durations = duration.getall()
                duration = 0
                for scene_duration in durations:
                    scene_duration = self.duration_to_seconds(scene_duration)
                    duration = duration + int(scene_duration)
                item['duration'] = str(duration)
            else:
                item['duration'] = None

            item['tags'] = []

            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Nathan Blake'
            item['parent'] = 'Nathan Blake'
            item['site'] = 'Nathan Blake'
            item['url'] = response.url
            item['id'] = re.search(r'.*/(\d+)?$', response.url).group(1)
            sceneurls = scenes
            item['scenes'] = []
            for sceneurl in sceneurls:
                if sceneurl.strip():
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'.*/(\d+)?$', sceneurl).group(1)})
            meta['movie'] = item

            if self.check_item(item, self.days):
                yield item
                for sceneurl in sceneurls:
                    yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()

        item['title'] = self.cleanup_title(response.xpath('//div[@class="nsVideoDetails"]/../following-sibling::div[1]/div[1]/div/text()').get().strip())

        scenedate = response.xpath('//div[contains(text(), "Release:")]/text()').get()
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)

        description = response.xpath('//div[contains(text(), "Description:")]/following-sibling::div/text()')
        if description:
            item['description'] = " ".join(description.getall())
        else:
            item['description'] = ""

        image = response.xpath('//video/@poster')
        if image:
            item['image'] = self.format_link(response, image.get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ""
            item['image_blob'] = ""

        item['director'] = 'Nethan Blake'

        item['performers'] = response.xpath('//div[contains(@id, "star") and contains(@id, "Movie")]/a/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))

        duration = response.xpath('//div[@class="nsVideoDetails"]/../following-sibling::div[1]/div[1]/div/span/text()')
        if duration:
            duration = duration.get().lower()
            duration = re.sub('[^0-9:]', '', duration)
            item['duration'] = self.duration_to_seconds(duration)
        else:
            item['duration'] = None

        tags = response.xpath('//div[@id="tagMovie"]/a/text()')
        if tags:
            item['tags'] = tags.getall()
        else:
            item['tags'] = []

        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]
        item['trailer'] = ''
        item['type'] = 'Scene'
        item['network'] = 'Nathan Blake'
        item['parent'] = 'Nathan Blake'
        item['site'] = 'Nathan Blake'

        item['url'] = response.url
        item['id'] = re.search(r'.*/(\d+)?$', response.url).group(1)
        yield item
