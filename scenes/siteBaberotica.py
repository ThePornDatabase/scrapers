import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBaberoticaSpider(BaseSceneScraper):
    name = 'Baberotica'
    network = 'AV Revenue'
    parent = 'Baberotica'
    site = 'Baberotica'

    start_urls = [
        'https://baberotica.com'
    ]

    selector_map = {
        'title': '//h1[@itemprop="name"]/span/following-sibling::text()',
        'performers': '//div[@class="video-info"]/p/span[@itemprop="actor"]/a/span/text()',
        'description': '//div[@itemprop="description"]/p/text()',
        'date': '//div[@class="container"]/meta[@itemprop="datePublished"]/@content',
        'image': '//div[@class="container"]/meta[@itemprop="thumbnailUrl"]/@content',
        'tags': '//div[@class="video-info"]/p/a[@itemprop="genre"]/text()',
        'external_id': r'.com\/(.*)\/',
        'trailer': '//div[@class="container"]/meta[@itemprop="contentUrl"]/@content',
        'pagination': '/girls-masturbating/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="border"]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Baberotica'})

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''

    def get_trailer(self, response):
        trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = "https:" + trailer
            return self.format_link(response, trailer)
        return ''
