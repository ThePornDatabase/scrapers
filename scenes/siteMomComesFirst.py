import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMomComesFirstSpider(BaseSceneScraper):
    name = 'MomComesFirst'
    network = 'Mom Comes First'
    parent = 'Mom Comes First'
    site = 'Mom Comes First'

    start_urls = [
        'https://momcomesfirst.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="entry-content"]/p/text()',
        'date': '//span[@class="published"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '',
        'tags': '//p[@class="post-meta"]/a/text()',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="et_pb_image_container"]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                image = self.format_link(response, image.get())
            else:
                image = None
            meta['image'] = image
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//p[contains(text(), "Starring")]/text()')
        if performers:
            performers = performers.get().replace("*", "").replace("Starring", "").strip()
            if "&" in performers:
                return performers.split(" & ")
            return [performers]
        return []

    def get_image_blob(self, response):
        image = response.meta['image']
        return self.get_image_blob_from_link(image)
