import re
import scrapy
import string
from datetime import datetime
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class MovieBrasileirinhasSpider(BaseSceneScraper):
    name = 'MovieBrasileirinhas'
    network = 'Brasileirinhas'
    parent = 'Brasileirinhas'

    start_urls = [
        'https://www.brasileirinhas.com.br'
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
        'pagination': '/filmes/pagina-%s.html'
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, dont_filter=True)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[contains(@class, "caixaFilme")]/a[1]/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "cenasLateral")]/div[contains(@class, "cenasFilme")]/@id').getall()
        if len(scenes) > 1:
            item = SceneItem()

            item['title'] = self.cleanup_title(response.xpath('//li[@class="breadcrumb-item active"]/text()').get().strip())

            item['date'] = datetime.today().strftime('%Y-%m-%d')

            description = response.xpath('//div[contains(@class,"textFilme")]//text()')
            if description:
                description = list(map(lambda x: x.strip(), description.getall()))
                item['description'] = self.translate_description(" ".join(description))
            else:
                item['description'] = ""

            image = response.xpath('//div[@class="grande"]/img[contains(@id, "frente")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            back = response.xpath('//div[@class="grande"]/img[contains(@id, "tras")]/@src')
            if back:
                item['back'] = self.format_link(response, back.get())
                item['back_blob'] = self.get_image_blob_from_link(item['back'])
            else:
                item['back'] = ""
                item['back_blob'] = ""

            item['performers'] = []

            item['tags'] = self.translate_tags(response.xpath('//div[contains(@class,"textTags")]/ul/li/a/text()').getall())

            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Brasileirinhas'
            item['parent'] = 'Brasileirinhas'
            item['site'] = 'Brasileirinhas'
            item['url'] = response.url
            item['id'] = re.search(r'.*/(.*?)\.htm', response.url).group(1)
            sceneurls = scenes
            item['scenes'] = []
            for sceneurl in sceneurls:
                if sceneurl.strip():
                    item['scenes'].append({'site': item['site'], 'external_id': re.search(r'(\d+)', sceneurl).group(1)})
            meta['movie'] = item

            yield item

    def translate_tags(self, tags):
        tag_return = []
        for tag in tags:
            tag = GoogleTranslator(source='pt', target='en').translate(tag.lower())
            tag = string.capwords(tag)
            tag_return.append(tag)
        return tag_return

    def translate_description(self, description):
        description = GoogleTranslator(source='pt', target='en').translate(description.lower())
        description = string.capwords(description)
        return description
