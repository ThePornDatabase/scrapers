import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VogovSpider(BaseSceneScraper):
    name = 'Vogov'
    network = 'Vogov'
    parent = 'Vogov'
    site = 'Vogov'

    start_urls = [
        'https://vogov.com'
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class,"info-video-description")]/p/text()',
        'performers': '//div[contains(@class,"info-video-models")]/a/text()',
        'date': '//li[contains(text(),"Release")]/span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class,"info-video-category")]/a/text()',
        'external_id': r'videos\/(.*)\/?',
        'trailer': '//script[contains(text(),"video_url")]/text()',
        'pagination': '/latest-videos/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="video-post"]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Vogov'})

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            trailer = re.search(r'video_url:\ .*?(https:\/\/.*?\.mp4)\/', trailer).group(1)
            if trailer:
                return trailer
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []
