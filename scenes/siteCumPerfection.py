import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class CumPerfectionSpider(BaseSceneScraper):
    name = 'CumPerfection'
    network = "Cum Perfection"
    parent = "Cum Perfection"

    start_urls = [
        'http://cum-fun.com'
    ]

    selector_map = {
        'title': '//span[contains(@class,"title_bar")]/text()',
        'description': '//span[@class="update_description"]/text()',
        'date': '//div[@class="gallery_info"]/div/div/div[contains(@class,"update_date")]/text()',
        'image': '//script[contains(text(),"thumbnail")]',
        'performers': '//div[@class="gallery_info"]/span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '//script[contains(text(),"thumbnail")]',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        trailer = self.process_xpath(
            response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search('path:\"(.*.mp4)\"', trailer)
            if trailer:
                trailer = trailer.group(1)
                trailer = trailer.replace(" ", "%20")
                trailer = "http://www.cum-fun.com/" + trailer
                return trailer
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('thumbnail:\"(.*.jpg)\"', image)
            if image:
                image = image.group(1)
                image = image.replace(" ", "%20")
                image = "http://www.cum-fun.com/" + image
                return self.format_link(response, image)
        return ''

    def get_site(self, response):
        return "Cum Perfection"
