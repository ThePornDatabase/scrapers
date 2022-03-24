import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAuntJudysSpider(BaseSceneScraper):
    name = 'AuntJudys'
    network = 'Aunt Judys'
    parent = 'Aunt Judys'

    start_urls = [
        'https://www.auntjudys.com',
        'https://www.auntjudysxxx.com',
    ]

    selector_map = {
        'title': '//span[contains(@class,"title_bar_hilite")]/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div[@class="table"]/div[@class="row"]/div[contains(@class,"update_date")]/text()[1]',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//div[@class="gallery_info"]/p/span[@class="update_models"]/a/text()',
        'tags': '//div[@class="gallery_info"]/span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//script[contains(text(),"df_movie")]/text()',
        're_trailer': '.*df_movie.*?path:\"(.*?.mp4)\"',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src0_3x').get()
            if not image:
                image = scene.xpath('./a/img/@src0_2x').get()
            if not image:
                image = scene.xpath('./a/img/@src0_1x').get()
            if not image:
                image = scene.xpath('./a/img/@src').get()
            if image:
                image = "https://www.auntjudys.com" + image.strip()
            else:
                image = ""

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'image': image})

    def get_site(self, response):
        if "xxx" in response.url:
            return "Aunt Judys XXX"
        return "Aunt Judys"

    def get_parent(self, response):
        if "xxx" in response.url:
            return "Aunt Judys XXX"
        return "Aunt Judys"

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                if trailer:
                    trailer = "https://www.auntjudys.com" + trailer.replace(" ", "%20")
                    return trailer

        return ''

    def get_id(self, response):
        externid = super().get_id(response)
        return externid.lower()
