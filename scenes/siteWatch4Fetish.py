import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWatch4FetishSpider(BaseSceneScraper):
    name = 'Watch4Fetish'
    network = 'Watch4Fetish'
    parent = 'Watch4Fetish'
    site = 'Watch4Fetish'

    start_urls = [
        'https://www.watch4fetish.com',
        #  Includes www.zentaidolls.com
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h4[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '//div[@class="video-info-details"]/span/i[contains(@class, "calendar")]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        'image_blob': True,
        're_image': r'poster=.*?\"(/content.*\.jpg)',
        'performers': '//div[@class="user-details-card-name"]/text()',
        'tags': '//h4[contains(text(),"Tags")]/following-sibling::a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=.*?\"(/trailer.*\.mp4)',
        'external_id': r'trailers/(.*?).html',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="video-post"]')
        for scene in scenes:
            altimage = scene.xpath('.//img/@src0_1x')
            if altimage:
                meta['altimage'] = self.format_link(response, altimage.get())
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers2 = []
        for performer in performers:
            if performer:
                performers2.append(string.capwords(performer))
        return performers2

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if not image:
            if "altimage" in meta:
                image = meta['altimage']
        return image

    def get_image_blob(self, response):
        meta = response.meta
        image = super().get_image(response)
        if not image or "/content/" not in image:
            if "altimage" in meta:
                image = meta['altimage']
        if image:
            image_blob = self.get_image_blob_from_link(image)
        else:
            image_blob = ''
        return image_blob
