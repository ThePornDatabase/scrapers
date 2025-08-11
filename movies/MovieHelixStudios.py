import re
import string
import scrapy
import unidecode
import html
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieHelixStudiosSpider(BaseSceneScraper):
    name = 'MovieHelixStudios'

    start_urls = [
        'https://www.helixstudios.com'
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
        'pagination': '/movies/page/%s'
    }

    def parse(self, response, **kwargs):
        meta = response.meta
        movies = self.get_movies(response)
        count = 0
        for movie in movies:
            count += 1
            meta['movie'] = movie
            yield movie

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] < 25:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[@class="grid-item-wrapper"]/a[1]/@href').getall()
        for movie in movies:
            movie_url = self.format_link(response, movie)
            yield scrapy.Request(movie_url, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        sceneurls = response.xpath('//div[@class="main"]//h2[contains(text(), "Videos on")]/following-sibling::div/a/@href').getall()
        sceneurls = list(filter(lambda x: len(x) > 0, sceneurls))
        if len(sceneurls) > 1:
            item = self.init_scene()
            item['network'] = 'Helix Studios'
            item['parent'] = 'Helix Studios'
            item['site'] = 'Helix Studios'
            item['url'] = response.url
            item['id'] = re.search(r'/(\d+)/', response.url).group(1)

            item['title'] = unidecode.unidecode(html.unescape(string.capwords(response.xpath('//div[@class="movie-header"]/h1/text()').get()).strip()))
            item['date'] = self.parse_date('today').strftime('%Y-%m-%d')

            submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], item['site'])
            if submitmovie:
                description = response.xpath('//div[@class="description-content"]/p/text()').getall()
                description = "".join(description)
                item['description'] = self.cleanup_description(description)

                image = response.xpath('//div[@class="movie-cover"]/img[contains(@src, "_front")]/@src')
                item['image'] = ''
                item['image_blob'] = ''
                if image:
                    item['image'] = image.get()
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                back = response.xpath('//div[@class="movie-cover"]/img[contains(@src, "_back")]/@src')
                item['back'] = ''
                item['back_blob'] = ''
                if back:
                    item['back'] = back.get()
                    item['back_blob'] = self.get_image_blob_from_link(item['back'])

                item['performers'] = response.xpath('//span[contains(text(), "Cast")]/following-sibling::div[@class="info-item-group"]/a/text()').getall()
                item['performers'] = list(map(lambda x: "".join(x).strip(), item['performers']))
                item['performers_data'] = self.get_performers_data(item['performers'])

                duration = response.xpath('//div[@class="info-items"]//span[contains(@class, "duration")]')
                if duration:
                    duration = duration.get()
                    duration = re.sub(r'[^0-9a-z]+', '', duration.lower())
                    duration = re.search(r'(\d)min', duration)
                    if duration:
                        item['duration'] = str(int(duration.group(1)) * 60)

                item['tags'] = ['Gay']

                item['trailer'] = ''
                item['type'] = 'Movie'

                item['scenes'] = []
                for sceneurl in sceneurls:
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'/(\d+)/', sceneurl).group(1)})

                yield item

    def get_performers_data(self, performers):
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Helix Studios"
                perf['site'] = "Helix Studios"
                performers_data.append(perf)
        return performers_data
