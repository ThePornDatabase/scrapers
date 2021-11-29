import scrapy
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
        'external_id': r'videos\/(\d+)\/?',
        'trailer': '//script[contains(text(),"video_url")]/text()',
        're_trailer': r'video_url:\ .*?(https:\/\/www\.fitting.*?\.mp4)',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"thumb videos")]/a')
        for scene in scenes:
            date = scene.xpath('./div[@class="main-info"]/div/p/text()').get()
            date = self.parse_date(date.strip()).isoformat()
            sceneurl = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta={'date': date})
