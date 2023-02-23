import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class DorcelClubSpider(BaseSceneScraper):
    name = 'BlueBirdFilmsMovie'
    network = 'Blue Bird Films'
    parent = 'Blue Bird Films'

    start_urls = [
        'https://www.bluebirdfilms.com'
    ]

    headers = {
        'Accept-Language': 'en-US,en',
        'x-requested-with': 'XMLHttpRequest',
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
        'pagination': '/vod/dvds/dvds_page_%s.html'
    }

    cookies = {
        'disclaimer2': 'xx'
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
        movies = response.xpath('//figure')
        for movie in movies:
            movieurl = self.format_link(response, movie.xpath('./a[1]/@href').get())
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        item = SceneItem()
        item['title'] = self.cleanup_title(response.xpath('//h2/text()').get().strip())
        item['description'] = ''
        image = response.xpath('//img[contains(@class, "dvd_box")]/@src0_2x').get()
        item['image'] = self.format_link(response, image.replace("//", "/"))
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ''
        director = response.xpath('//div[@class="director"]/text()')
        if director:
            director = director.get()
            if ":" in director:
                director = re.search(r'\:\s+?(.*)', director).group(1).strip()
        item['director'] = ''
        item['performers'] = response.xpath('//div[contains(@class, "modelnames") and contains(text(), "Featuring")]/a/text()').getall()
        item['performers'] = list(map(lambda x: self.cleanup_title(x.strip()), item['performers']))
        item['tags'] = []
        item['trailer'] = ''
        item['date'] = None
        item['type'] = 'Movie'
        item['network'] = 'Blue Bird Films'
        item['parent'] = 'Blue Bird Films'
        item['site'] = 'Blue Bird Films'
        item['store'] = 'Blue Bird Films'
        item['url'] = response.url
        item['id'] = re.search(r'.*/(.*)\.htm', response.url).group(1)
        item['scenes'] = []
        meta['scenes'] = []
        scenes = response.xpath('//figure[contains(@class, "setVideoThumb")]')
        item['duration'] = '0'

        date_url = "https://www.bluebirdfilms.com/vod/" + response.xpath('//figure[contains(@class, "setVideoThumb")]/a/@href').get()
        date_text = requests.get(date_url)
        date_text = date_text.text.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "")
        scene_date = re.search(r'ReleaseDate.*?(\d{1,2}/\d{1,2}/\d{4})', date_text)
        if scene_date:
            item['date'] = self.parse_date(scene_date.group(1), date_formats=['%d/%m/%Y']).isoformat()

        for scene in scenes:
            scene_item = {}
            scene_item['scene_url'] = "https://www.bluebirdfilms.com/vod/" + scene.xpath('./a/@href').get()
            scene_item['scene_id'] = scene.xpath('./@id').get()
            scene_duration = scene.xpath('.//i[contains(@class, "glyphicon-time")]/following-sibling::comment()')
            if scene_duration:
                scene_duration = scene_duration.get()
                scene_duration = scene_duration.replace("s", "").replace("m", "")
                scene_duration = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', scene_duration).group(1)
                scene_item['scene_duration'] = self.duration_to_seconds(scene_duration)
                item['duration'] = str(int(item['duration']) + int(scene_item['scene_duration']))
            scene_item['scene_trailer'] = scene.xpath('.//source/@src').get()

            scene_item['scene_image'] = None
            scene_image = scene.xpath('.//picture/img/@src0_2x')
            if scene_image:
                scene_image = self.format_link(response, scene_image.get()).replace("content//", "content/")
            if not scene_image:
                scene_image = scene.xpath('.//picture/img/@src0_1x')
                if scene_image:
                    scene_image = self.format_link(response, scene_image.get()).replace("content//", "content/")
            if not scene_image:
                scene_image = scene.xpath('.//picture/img/@src0_3x')
                if scene_image:
                    scene_image = self.format_link(response, scene_image.get()).replace("content//", "content/")
            if not scene_image:
                scene_image = scene.xpath('.//picture/img/@src')
                if scene_image:
                    scene_image = self.format_link(response, scene_image.get()).replace("content//", "content/")

            if scene_image:
                scene_item['scene_image'] = scene_image

            item['scenes'].append({'site': item['site'], 'external_id': scene_item['scene_id']})
            meta['scenes'].append(scene_item)
        meta['movie'] = item
        yield self.check_item(item, self.days)

        for sceneurl in meta['scenes']:
            meta['currscene'] = sceneurl
            yield scrapy.Request(self.format_link(response, sceneurl['scene_url']), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        currscene = meta['currscene']
        item = SceneItem()

        item['url'] = currscene['scene_url']
        item['trailer'] = currscene['scene_trailer']
        item['duration'] = currscene['scene_duration']
        item['id'] = currscene['scene_id']
        if currscene['scene_image']:
            item['image'] = currscene['scene_image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = None
            item['image_blob'] = None

        item['type'] = 'Scene'

        title = response.xpath('//h3[@class="mb-5"]//text()').getall()
        item['title'] = self.cleanup_title(" ".join(title).replace("  ", " "))
        item['title'] = item['title'].replace("( ", "(").replace(" )", ")")

        scenedate = response.xpath('//td[contains(text(), "Date:")]/following-sibling::td/text()')
        if scenedate:
            scenedate = scenedate.get()
            item['date'] = self.parse_date(scenedate, date_formats=['%d/%m/%Y']).isoformat()
        else:
            item['date'] = ''

        item['description'] = item['title']
        item['director'] = ''
        item['performers'] = response.xpath('//span[contains(@class, "update_models")]/a/text()').getall()
        item['performers'] = list(map(lambda x: self.cleanup_title(x.strip()), item['performers']))

        item['tags'] = response.xpath('//td[contains(text(), "Tags:")]/following-sibling::td/a/text()').getall()
        item['tags'] = list(map(lambda x: self.cleanup_title(x.strip()), item['tags']))

        item['network'] = 'Blue Bird Films'
        item['parent'] = 'Blue Bird Films'
        item['site'] = 'Blue Bird Films'
        yield self.check_item(item, self.days)
