import dateparser
import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class FittingRoomSpider(BaseSceneScraper):
    name = 'FittingRoom'
    network = 'Fitting Room'
    parent = 'Fitting Room'
    site = 'Fitting Room'

    start_urls = [
        'https://www.fitting-room.com/'
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': "",
        'performers': '//div[@class="info-model"]/p[@class="name"]/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//meta[@property="article:tag"]/@content',
        'external_id': 'videos\/(\d+)\/?',
        'trailer': '//script[contains(text(),"video_url")]/text()',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"thumb videos")]/a')
        for scene in scenes:
            date = scene.xpath('./div[@class="main-info"]/div/p/text()').get()
            date = dateparser.parse(date.strip()).isoformat()            
            sceneurl = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene,  meta={'date': date})

    def get_description(self, response):
        return ''

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = re.search('video_url:\ .*?(https:\/\/www\.fitting.*?\.mp4)', trailer).group(1)
                if trailer:
                    return trailer
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []
