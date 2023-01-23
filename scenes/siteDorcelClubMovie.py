import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class DorcelClubSpider(BaseSceneScraper):
    name = 'DorcelClubMovie'
    network = 'Dorcel Club'
    parent = 'Dorcel Club'

    start_urls = [
        'https://www.dorcelclub.com'
    ]

    headers = {
        'Accept-Language': 'en-US,en',
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
        'pagination': '/movies/more?lang=en&page=%s'
    }

    cookies = {
        # ~ 'dorcelclub': 'jjp5ajprrugqqp7j04ibtugdlp',
        # ~ 'u': '61836d0b0c409b94e77',
        'disclaimer2': 'xx'
    }

    def start_requests(self):
        yield scrapy.Request("https://www.dorcelclub.com/en/", callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

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
        movies = response.xpath('//a[@class="movie thumbnail"]/@href').getall()
        for movie in movies:
            movieurl = self.format_link(response, movie)
            yield scrapy.Request(movieurl, callback=self.parse_movie, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//span[@class="scenes"]/text()').get()
        scenes = int(re.search(r'\:\s+?(\d+)', scenes).group(1))
        if scenes > 1:
            item = SceneItem()
            item['title'] = self.cleanup_title(response.xpath('//h1/text()').get().strip())
            scenedate = response.xpath('//span[@class="out_date"]/text()').get()
            scenedate = re.search(r'(\d{4})', scenedate).group(1).strip()
            scenedate = scenedate + "-01-01"
            item['date'] = self.parse_date(scenedate).isoformat()
            item['description'] = ''
            images = response.xpath('//div[@class="header"]//source[contains(@media, "max-width") and contains(@data-srcset, "cover")]/@data-srcset').getall()
            images = sorted(images, reverse=True)
            image = images[0]
            item['image'] = re.search(r'(.*?) 1x', image).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ''
            director = response.xpath('//div[@class="director"]/text()')
            if director:
                director = director.get()
                if ":" in director:
                    director = re.search(r'\:\s+?(.*)', director).group(1).strip()
            if director:
                item['director'] = director
            else:
                item['director'] = ''
            item['performers'] = response.xpath('//div[contains(@class, "actor thumbnail")]/a/div/text()').getall()
            item['performers'] = list(map(lambda x: x.strip(), item['performers']))
            duration = response.xpath('//span[@class="duration"]/text()')
            if duration:
                duration = duration.get().lower()
                hours = ''
                minutes = ''
                seconds = ''
                if "h" in duration:
                    hours = (int(re.search(r'(\d{1,2})h', duration).group(1)) * 3600)
                    if "m" not in duration:
                        minutes = re.search(r'h\s+?(\d{1,2})', duration)
                        if minutes:
                            minutes = minutes.group(1)
                else:
                    hours = 0
                if "m" in duration and not minutes:
                    minutes = re.search(r'(\d{1,2})m', duration)
                    if minutes:
                        minutes = minutes.group(1)
                    else:
                        minutes = 0
                seconds = re.search(r'm(\d{1,2})', duration)
                if seconds:
                    seconds = seconds.group(1)
                else:
                    seconds = 0
                if minutes:
                    minutes = int(minutes) * 60
                else:
                    minutes = 0
                if seconds:
                    seconds = int(seconds)
                else:
                    seconds = 0
                item['duration'] = str(hours + minutes + seconds)
            else:
                item['duration'] = None
            item['tags'] = []
            item['trailer'] = ''
            item['type'] = 'Movie'
            item['network'] = 'Dorcel Club'
            item['parent'] = 'Dorcel Club'
            item['site'] = 'Dorcel Club'
            item['url'] = response.url
            item['id'] = re.search(r'movie/.*?/.*?/(\d+)', item['image']).group(1)
            sceneurls = response.xpath('//div[@class="scenes"]/div/div/a/@href').getall()
            item['scenes'] = []
            for sceneurl in sceneurls:
                item['scenes'].append({'site': item['site'], 'external_id': re.search(r'scene/(\d+)/', sceneurl).group(1)})
            meta['movie'] = item
            yield item
            for sceneurl in sceneurls:
                yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        item['title'] = self.cleanup_title(response.xpath('//h1[@class="title"]/text()').get().strip())
        scenedate = response.xpath('//span[@class="publish_date"]/text()')
        if scenedate:
            scenedate = scenedate.get()
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
        else:
            item['date'] = self.parse_date('today').isoformat()
        description = response.xpath('//div[@class="content-text"]/span[@class="full"]//text()|//div[@class="content-text"]/span[@class="small"]//text()|//div[@class="content-text"]/p/text()')
        if description:
            item['description'] = description.get().strip()
        else:
            item['description'] = ''
        item['image'] = ''
        images = response.xpath('//div[contains(@class,"player_container")]//source[contains(@media, "max-width")]/@data-srcset')
        if images:
            images = images.getall()
            images = sorted(images, reverse=True)
            image = images[0]
            item['image'] = re.search(r'(.*?) 1x', image).group(1)
        else:
            image = response.xpath('//script[contains(text(), "VodPlayer")]/text()')
            if image:
                image = re.search(r'image\:.*?(http.*?)\"', image.get())
                if image:
                    item['image'] = self.get_image(image.group(1))
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ''
        item['director'] = movie['director']
        item['performers'] = response.xpath('//div[@class="actress"]/a/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))
        item['tags'] = []
        item['trailer'] = ''
        item['type'] = 'Scene'
        item['network'] = 'Dorcel Club'
        item['parent'] = 'Dorcel Club'
        item['site'] = 'Dorcel Club'
        duration = response.xpath('//span[@class="duration"]/text()')
        if duration:
            duration = duration.get().lower()
            if "h" in duration:
                hours = (int(re.search(r'(\d{1,2})h', duration).group(1)) * 3600)
            else:
                hours = 0
            minutes = re.search(r'(\d{1,2})m', duration)
            if minutes:
                minutes = minutes.group(1)
            else:
                minutes = 0
            seconds = re.search(r'm(\d{1,2})', duration)
            if seconds:
                seconds = seconds.group(1)
            else:
                seconds = 0
            item['duration'] = str(hours + (int(minutes) * 60) + int(seconds))
        else:
            item['duration'] = None

        item['url'] = response.url
        item['id'] = re.search(r'scene/(\d+)', response.url).group(1)
        yield item

    def get_image(self, image):
        trash = '_' + image.split('_', 3)[-1].rsplit('.', 1)[0]
        image = image.replace(trash, '', 1)
        return image
