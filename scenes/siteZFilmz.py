import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteZFilmzSpider(BaseSceneScraper):
    name = 'ZFilmz'
    network = 'Z-Films'

    start_urls = [
        'https://www.z-filmz-originals.com',
    ]

    selector_map = {
        'title': '//h1[@class="info-section--title"]/text()',
        'description': '//div[@class="inner"]/div/p[1]/text()',
        'date': '//i[@class="fas fa-calendar"]/following-sibling::span/text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@title="Models"]/span/a/text()',
        'tags': '//span[@title="Categories"]/span/a/text()',
        'external_id': r'updates\/(.*).html',
        'trailer': '//meta[@name="twitter:player:stream"]/@content',
        'pagination': '/en/collections/page/%s?media=video'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="control-card"]/div[@class="card-btns"]/a[2]')
        for scene in scenes:
            sceneid = scene.xpath('./@data-collection').get()
            scene = scene.xpath('./@href').get()
            if sceneid and scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'id': sceneid})

    def get_site(self, response):
        return "Z-Films"

    def get_parent(self, response):
        return "Z-Filmz"

    def get_image(self, response):
        image = super().get_image(response)
        if "jpg?" in image:
            image = re.search(r'(.*)\?', image).group(1)
        return image
