import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SpankmonsterSpider(BaseSceneScraper):
    name = 'Spankmonster'
    network = 'Spankmonster'
    parent = 'Spankmonster'
    site = 'Spankmonster'

    start_urls = [
        'https://Spankmonster.com'
    ]


    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//h1[@class="description"]/text()',
        'performers': '//a[@data-Label="Performer" or @data-label="Performer"]/span/span/text()',
        'date': '//div[@class="release-date"]/span[contains(text(),"Released")]/following-sibling::text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': '\/(\d+)\/',
        'trailer': '',
        'pagination': '/watch-newest-spank-monster-clips-and-scenes.html?page=%s&view=grid'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="animated-screenshot-container"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Spankmonster'})

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []
