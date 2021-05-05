import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class SexMexSpider(BaseSceneScraper):
    name = 'SexMex'
    network = 'SexMex'
    parent = 'SexMex'
    site = 'SexMex'

    start_urls = [
        'https://sexmex.xxx/'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': 'updates\/(.*)\.html$',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumbnail"]')
        for scene in scenes:
            date = scene.xpath('./div/p[@class="scene-date"]/text()').get()
            date = dateparser.parse(date.strip()).isoformat()            
            title = scene.xpath('./div/h5/a/text()').get()
            if " . " in title:
                title = re.search('^(.*)\ \.\ ', title).group(1).strip()
            description = scene.xpath('./div/p[@class="scene-descr"]/text()').get()
            image = 'https://sexmex.xxx/tour/' + scene.xpath('./a/img/@src').get()
            performers = scene.xpath('./div/p[@class="cptn-model"]/a/text()').getall()
            
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                    meta={'date': date, 'title': title, 'description': description, 'image': image, 'performers': performers})


