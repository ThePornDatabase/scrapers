import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviePrivateSpider(BaseSceneScraper):
    name = 'MoviePrivate'
    network = "Private"

    start_urls = [
        'https://www.private.com',
    ]

    selector_map = {
        'external_id': r'/(\d+)$',
        'pagination': '/movies/%s/'
    }

    def parse(self, response, **kwargs):
        meta = response.meta
        movies = self.get_movies(response)
        count = 0
        for movie in movies:
            count += 1
            meta['movie'] = movie
            yield movie
        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        movies = response.xpath('//div[@class="film"]/a/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scene"]//h3/a/text()').get()
        if len(scenes) > 1:
            item = SceneItem()
            item['title'] = self.cleanup_title(response.xpath('//meta[@itemprop="name"]/@content|//h1[@itemprop="name"]/text()').get().strip())
            scenedate = response.xpath('//meta[@itemprop="uploadDate"]/@content|//em[contains(text(), "Release date")]/following-sibling::span[1]/text()').get()
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            description = response.xpath('//meta[@itemprop="description"]/@content|//meta[@property="og:description"]/@content')
            if description:
                item['description'] = self.cleanup_description(description.get())
            else:
                item['description'] = ''
            item['image'] = response.xpath('//div[contains(@class, "dvds-photo")]/a/picture/source[1]/@srcset').get()
            if re.search(r'( \d+w)', item['image']):
                item['image'] = re.sub(r'( \d+w)', '', item['image'])
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ''
            director = response.xpath('//p[@class="director"]/span/text()')
            if director:
                director = director.get()
            if director:
                item['director'] = director
            else:
                item['director'] = ''
            item['performers'] = response.xpath('//p[@class="dvd-performers"]/span/a/span/text()').getall()
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))
            duration = response.xpath('//em[contains(text(), "Duration")]/following-sibling::text()')
            item['duration'] = None
            if duration:
                duration = duration.get().lower()
                duration = re.search(r'(\d+) [Mm]in', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = str(int(duration) * 60)
            item['tags'] = []
            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Private'
            item['parent'] = 'Private'
            item['site'] = 'Private'
            item['url'] = response.url
            item['id'] = re.search(r'movie/(\d+).*', response.url).group(1)
            if item['id'] == '1681':
                item['id'] = '16811'
            sceneurls = response.xpath('//div[@class="scene"]//h3/a/@href').getall()
            item['scenes'] = []
            for sceneurl in sceneurls:
                item['scenes'].append({'site': item['site'], 'external_id': re.search(r'.*/(\d+)', sceneurl).group(1)})
            meta['movie'] = item
            yield item
            for sceneurl in sceneurls:
                yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        item['title'] = self.cleanup_title(response.xpath('//meta[@itemprop="name"]/@content').get().strip())
        scenedate = response.xpath('//meta[@itemprop="uploadDate"]/@content')
        item['date'] = ""
        if scenedate:
            scenedate = scenedate.get()
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
        item['description'] = response.xpath('//meta[@itemprop="description"]/@content').get().strip()
        item['image'] = ''
        item['image'] = response.xpath('//meta[@itemprop="thumbnailUrl"]/@content').get()
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ''
        item['director'] = movie['director']
        item['performers'] = response.xpath('//ul[@class="scene-models-list"]/li/a[@data-track="PORNSTAR_NAME"]/text()|//ul[@class="scene-models-list-tags-sites"]/li[contains(@class, "tag-models")]/a/text()').getall()
        item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
        item['tags'] = response.xpath('//ul[contains(@class,"scene-tags")]/li/a/text()').getall()
        item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))
        item['trailer'] = ''
        item['type'] = 'Scene'
        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]
        item['network'] = 'Private'
        item['parent'] = self.get_site(response)
        item['site'] = self.get_site(response)
        item['url'] = response.url
        item['id'] = re.search(r'.*/(\d+)', response.url).group(1)
        yield item

    def get_image(self, image):
        trash = '_' + image.split('_', 3)[-1].rsplit('.', 1)[0]
        image = image.replace(trash, '', 1)
        return image

    def get_site(self, response):
        site = response.xpath('//span[@class="title-site"]/text()').get()
        if site:
            return site.strip()
        elif "privateblack" in response.url:
            return "Private Black"
        return "Private"

    def get_parent(self, response):
        site = response.xpath('//span[@class="title-site"]/text()').get()
        if site:
            return site.strip()
        elif "privateblack" in response.url:
            return "Private Black"
        return "Private"
