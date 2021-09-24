import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class JavBusSpider(BaseSceneScraper):
    name = 'JavBus'
    network = 'JavBus'
    parent = 'JavBus'

    start_urls = [
        'https://www.javbus.com'
    ]

    selector_map = {
        'title': "#videos_page-page h1::text",
        'date': '//div[@class="col-md-3 info"]/p[2]/text()',
        'image': '//a[contains(@href, "/cover/")]/@href | //a[@class="sample-box"]/div/img/@src',
        'performers': '//a[@class="avatar-box"]//span/text()',
        'tags': '//span[@class="genre"]/a[contains(@href, "/genre/")]/text()',
        'external_id': '\\/([0-9A-Za-z_-]+)$',
        'trailer': '',
        'pagination': '/en/uncensored/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.css(".movie-box::attr(href)").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        return response.xpath(
            '//p/a[contains(@href, "/studio/")]/text()').get().strip()

    def get_title(self, response):
        title = response.xpath(
            '//head/title/text()').get().strip().replace(' - JavBus', '')
        externid = self.get_id(response)
        if externid.replace('-', '').replace('_', '').replace(' ', '').isdigit():
            title = self.get_site(response) + ' ' + title
            title = title.replace(externid + ' ', '')

        return title
