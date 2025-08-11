import re
import html
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieJMEliteSpider(BaseSceneScraper):
    name = 'MovieJMElite'

    start_urls = [
        'https://www.jacquieetmichelelite.com'
    ]

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 120,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    cookies = {
        'dscl': '1',
        'ppndr': '1',
        'promo-widget-head': '1',
        'force-my18pass-refresh': '0',
    }

    selector_map = {
        'title': '//h1[contains(@class,"video-detail__title")]/text()',
        'description': '//div[contains(@class,"video-detail__description")]/text()',
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'duration': '//script[contains(@type, "json")]/text()',
        're_duration': r'duration.*?T(.*?)\"',
        'image': '//img[contains(@class,"video-detail") and contains(@class, "poster")]/@src',
        'performers': '//p[contains(@class,"actor-item") and contains(@class,"title")]/text()',
        'tags': '',
        'studio': '//strong[contains(text(), "Studio:")]/following-sibling::a/text()',
        'director': '//ul[@class="video-detail__infos"]/li[3]/text()',
        'external_id': r'elite/(\d+)/',
        # ~ 'pagination': '/en/porn-movies-p-%s.html'
        'pagination': '/en/porn-movies-jacquie-et-michel-elite-f-1354-p-%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath(
            '//a[@class="video-item"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_movie, cookies=self.cookies, headers=self.headers, meta=meta)

    def parse_movie(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="scene-item"]/@href').getall()
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['date'] = self.get_date(response)
        item['description'] = self.get_description(response)
        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['director'] = self.get_director(response)
        item['performers'] = self.get_performers(response)
        item['duration'] = self.get_duration(response)
        item['tags'] = []
        item['trailer'] = ''
        item['type'] = 'Movie'
        studio = response.xpath('//strong[contains(text(), "Studio:")]/following-sibling::a/text()')
        if studio:
            item['site'] = studio.get()
        else:
            item['site'] = 'Jacquie et Michel Elite'
        item['network'] = item['site']
        item['parent'] = item['site']
        item['store'] = 'Jacquie et Michel Elite'
        item['url'] = response.url
        item['id'] = re.search(r'elite/(\d+)/', response.url).group(1)
        item['scenes'] = []
        for sceneurl in scenes:
            item['scenes'].append({'site': item['site'], 'external_id': re.search(r'show/(\d+)/', sceneurl).group(1)})
        meta['movie'] = item
        yield item
        for sceneurl in scenes:
            yield scrapy.Request(self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        movie = meta['movie']
        item = SceneItem()
        jsondata = response.xpath('//script[contains(text(), "datePublished")]/text()').get()
        item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', response.xpath('//h1[contains(@class, "title")]/text()').get().strip())))
        item['date'] = re.search(r'datePublished.*?(\d{4}-\d{2}-\d{2})', jsondata).group(1)
        description = response.xpath('//div[contains(@class,"description") and contains(@class,"video-detail")]/text()')
        if description:
            item['description'] = description.get().strip()
        else:
            item['description'] = ''
        image = response.xpath('//video/@poster')
        if image:
            item['image'] = image.get()
        else:
            item['image'] = None
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['director'] = movie['director']
        item['performers'] = response.xpath('//p[contains(@class,"actor-item") and contains(@class,"title")]/text()').getall()
        item['performers'] = list(map(lambda x: x.strip(), item['performers']))
        item['tags'] = []
        item['trailer'] = ''
        item['type'] = 'Scene'
        item['network'] = 'Jacquie et Michel'
        item['parent'] = 'Jacquie et Michel Elite'
        studio = response.xpath('//strong[contains(text(), "Studio:")]/following-sibling::a/text()')
        if studio:
            item['site'] = studio.get()
        else:
            item['site'] = 'Jacquie et Michel Elite'
        duration = re.search(r'duration.*?(T\d.*?S)', jsondata)
        if duration:
            duration = duration.group(1)
            item['duration'] = self.duration_to_seconds(duration)
        else:
            item['duration'] = None

        item['url'] = response.url
        item['id'] = re.search(r'show/(\d+)/', response.url).group(1)
        yield item
