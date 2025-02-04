import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviePrivateClassicsSpider(BaseSceneScraper):
    name = 'MoviePrivateClassics'
    network = "Private"

    start_urls = [
        'https://www.privateclassics.com',
    ]

    selector_map = {
        'external_id': r'/(\d+)/$',
        'pagination': '/en/movies/%s/'
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
        movies = response.xpath('//article[contains(@class, "video")]')
        for movie in movies:
            imagealt = movie.xpath('./figure/a/img/@data-src')
            if imagealt:
                meta['imagealt'] = imagealt.get()
            movie = movie.xpath('./figure/a/@href').get()
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[contains(@class,"site-movies")]/li//article/figure/a/@href').get()
        if len(scenes) > 1:
            item = SceneItem()
            item['title'] = self.cleanup_title(response.xpath('//div[@class="container"]/div[@class="product"][1]/h1/text()').get().strip())
            scenedate = response.xpath('//p[contains(@class, "release")]//text()').getall()
            scenedate = "".join(scenedate)
            scenedate = re.sub('[^a-zA-Z0-9-/]', '', scenedate)
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = ''
            description = response.xpath('//div[@class="container"]//p[contains(@class, "sinopsys")]/text()')
            if description:
                item['description'] = description.get().strip()
            else:
                item['description'] = ""
            item['image'] = response.xpath('//div[@class="content-cover"]/img/@src').get()
            if not item['image']:
                item['image'] = meta['imagealt']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ''
            director = response.xpath('//h4[@class="directe-by"]/text()')
            if director:
                director = director.get()
                if ":" in director:
                    director = re.search(r':(.*)', director).group(1)
            if director:
                item['director'] = director.strip()
            else:
                item['director'] = ''
            item['performers'] = response.xpath('//ul[@class="featured"]//a/span/text()').getall()
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))
            item['performers'] = list(filter(None, item['performers']))
            duration = response.xpath('//em[contains(text(), "Duration")]/following-sibling::text()')
            item['duration'] = None
            durations = response.xpath('//span[@class="scene-length-start"]/following-sibling::text()').getall()
            if durations:
                duration = 0
                for entry in durations:
                    minutes = re.search(r'(\d+) [Mm]in', entry)
                    if minutes:
                        duration = duration + int(minutes.group(1))
                if duration:
                    item['duration'] = str(duration * 60)

            item['tags'] = []
            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Private'
            item['parent'] = 'Private'
            item['site'] = 'Private'
            item['url'] = response.url
            item['id'] = re.search(r'.*/(\d+)/', response.url).group(1)
            scenes = response.xpath('//article[contains(@class, "content video")]')
            scenelist = []
            for scene in scenes:
                sceneurl = scene.xpath('.//figure/a/@href').get()
                sceneduration = scene.xpath('.//span[@class="scene-length-start"]/following-sibling::text()[contains(., "min")]')
                if sceneduration:
                    sceneduration = re.sub('[^a-zA-Z0-9-/]', '', sceneduration.get())
                    sceneduration = re.search(r'(\d+)min', sceneduration).group(1)
                    sceneduration = str(int(sceneduration) * 60)
                scenelist.append({'url': sceneurl, 'duration': sceneduration})
            item['scenes'] = []
            for sceneurl in scenelist:
                extern_id = re.search(r'.*/(\d+)', sceneurl['url']).group(1)
                item['scenes'].append({'site': "Private Classics", 'external_id': extern_id})
            meta['movie'] = item
            yield item
            for sceneurl in scenelist:
                meta['duration'] = sceneurl['duration']
                yield scrapy.Request(self.format_link(response, sceneurl['url']), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        item['title'] = self.cleanup_title(response.xpath('//div[@class="container"]/div[@class="product"][1]/h1/text()').get().strip())
        item['date'] = movie['date']
        description = response.xpath('//div[contains(@class, "user-tools")]/p/text()')
        if description:
            item['description'] = description.get().strip()
        else:
            item['description'] = ""

        item['image'] = ''
        item['image'] = response.xpath('//meta[@itemprop="thumbnailUrl"]/@content|//meta[@property="og:image"]/@content|//div[@id="video_player_finished"]/img/@src').get()
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ''
        item['director'] = movie['director']
        item['performers'] = response.xpath('//ul[@class="featured"]//a//text()').getall()
        item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
        item['performers'] = list(filter(None, item['performers']))
        item['tags'] = []
        item['trailer'] = ''
        if isinstance(meta['duration'], str):
            item['duration'] = meta['duration']
        item['type'] = 'Scene'
        item['movies'] = [{'site': movie['site'], 'external_id': movie['id']}]
        item['network'] = 'Private'
        item['parent'] = "Private Classics"
        item['site'] = "Private Classics"
        item['url'] = response.url
        item['id'] = re.search(r'.*/(\d+)', response.url).group(1)
        yield item
