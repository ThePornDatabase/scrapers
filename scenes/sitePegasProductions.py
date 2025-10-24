import re
import json
import string
import unicodedata
import scrapy
import time
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SitePegasProductionsSpider(BaseSceneScraper):
    name = 'PegasProductions'
    network = 'Pegas Productions'
    parent = 'Pegas Productions'
    site = 'Pegas Productions'

    start_urls = [
        'https://www.pegasproductions.com',
    ]

    cookies = {
        'langue': 'en',
        'consent': 'true',
        'Niche': 'Pegas',
        'AB': 'A',
        'limiteouvert': '0',
        'bypass-disclaimer': '1'
    }

    selector_map = {
        'title': '//div[@class="span10"]/h4/text()',
        'description': '//div[@class="span10"]//h5/following-sibling::p[1]/text()',
        'image': '//script[contains(text(), "poster")]/text()',
        're_image': r'(http.*?\.jpg)',
        'performers': '//div[contains(@id,"synopsis-next-to-video")]//a[@itemprop="actor"]/text()',
        'tags': '//div[@class="span9"]/h4/strong[contains(text(), "Tags")]/following-sibling::text()',
        'external_id': r'\.com/(.*)\?',
        'trailer': '//script[contains(text(), "poster")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'pagination': '/wp-json/wp/v2/posts?per_page=24&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            blocklist = [8204, 1, 8108, 9742, 88, 8005, 11669, 11659, 9747, 8951]
            if not any(val in scene['categories'] for val in blocklist):
                meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
                meta['id'] = scene['slug']
                meta['url'] = scene['link']
                meta['orig_title'] = scene['title']['rendered']
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta, cookies=self.cookies)

    def get_tags(self, response):
        tags = response.xpath(self.get_selector_map('tags'))
        if tags:
            tags = tags.get()
            tags = tags.split(",")
            tags = list(map(lambda x: x.strip().title(), tags))
            tags = [i for i in tags if i]
            return tags
        return []

    def get_title(self, response):
        meta = response.meta
        title = super().get_title(response)
        if not title:
            title = meta['orig_title']
        return self.strip_accents(title)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(map(lambda x: self.strip_accents(x), performers))
        return performers

    def strip_accents(self, text):
        try:
            text = unicode(text, 'utf-8')
        except (TypeError, NameError):  # unicode is a default on python 3
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        text = re.sub('[^0-9a-zA-Z ]', '', text)
        return string.capwords(str(text))

    def get_image(self, response):
        image = super().get_image(response)
        if "jpg" not in image:
            image = response.xpath('//meta[@itemprop="thumbnailUrl"]/@content').get()
            image = image.replace("screenshots", "screenshots/")
        return image

    def get_duration(self, response):
        duration = response.xpath('//p[contains(text(), "duration:")]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9:]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None
