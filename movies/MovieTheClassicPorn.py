import re
import string
import scrapy
import unidecode
import html
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieTheClassicPornSpider(BaseSceneScraper):
    name = 'MovieTheClassicPorn'

    start_urls = [
        'https://theclassicporn.com'
    ]

    selector_map = {
        'external_id': r'/(\d+)/',
        'trailer': '',
        'pagination': '/videos/<PAGE>/?vcidss=1528,6260,12287&vcids=all|&sort_by=post_date%20desc'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'CONCURRENT_REQUESTS_PER_IP': 2,
        "MEDIA_ALLOW_REDIRECTS": True,
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination').replace("<PAGE>", str(page)))

    def parse(self, response, **kwargs):
        meta = response.meta
        movies = self.get_movies(response)
        count = 0
        for movie in movies:
            count += 1
            meta['movie'] = movie
            yield movie

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        movies = response.xpath('//div[@class="video-list-item"]')
        for movie in movies:
            item = SceneItem()
            item['network'] = 'The Classic Porn'
            item['parent'] = 'The Classic Porn'
            item['site'] = 'The Classic Porn'
            item['url'] = "https://theclassicporn.com" + movie.xpath('./div[1]/a[1]/@href').get()
            item['id'] = re.search(r'/(\d+)/', item['url']).group(1)

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(movie.xpath('.//p[@class="title"]/a/text()').get()).strip()))

            scenedate = movie.xpath('.//span[contains(text(), "Year")]/following-sibling::a/text()').get()
            item['date'] = '1970-01-01'
            if scenedate:
                scenedate = re.search(r'(\d{4})', scenedate)
                if scenedate:
                    item['date'] = scenedate.group(1) + "-01-01"

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:
                item['description'] = ""

                image = movie.xpath('.//img[@class="thumb"]/@src')
                item['image'] = ''
                item['image_blob'] = ''
                if image and "https" in image.get():
                    item['image'] = image.get()
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['performers'] = []
                item['performers_data'] = []

                performers = movie.xpath('.//span[contains(text(), "Actress")]/following-sibling::a/text()').getall()
                for performer in performers:
                    performer = string.capwords(performer.strip())
                    performer_extra = {}
                    performer_extra['name'] = performer
                    performer_extra['site'] = "The Classic Porn"
                    performer_extra['extra'] = {}
                    performer_extra['extra']['gender'] = "Female"
                    item['performers_data'].append(performer_extra)
                    item['performers'].append(performer)

                performers = movie.xpath('.//span[contains(text(), "Actors")]/following-sibling::a/text()').getall()
                for performer in performers:
                    performer = string.capwords(performer.strip())
                    performer_extra = {}
                    performer_extra['name'] = performer
                    performer_extra['site'] = "The Classic Porn"
                    performer_extra['extra'] = {}
                    performer_extra['extra']['gender'] = "Male"
                    item['performers_data'].append(performer_extra)
                    item['performers'].append(performer)

                duration = movie.xpath('.//span[contains(text(), "Duration")]/following-sibling::text()')
                if duration:
                    duration = duration.get().lower().replace(" ", "")
                    item['duration'] = str(int(re.search(r'(\d{1,2})min', duration).group(1)) * 60)
                else:
                    item['duration'] = None

                director = movie.xpath('.//span[contains(text(), "Director")]/following-sibling::a/text()')
                if director:
                    item['director'] = director.get()
                    item['director'] = item['director'].replace("\r", "").replace("\n", "").replace("\t", "").strip()

                item['tags'] = ["Classic Porn"]

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []

                if self.check_item(item, self.days):
                    yield item
