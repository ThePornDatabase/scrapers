import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CXWowSpider(BaseSceneScraper):
    name = 'CXWow'
    network = 'CX Wow'

    start_urls = [
        'https://www.becomingfemme.com/',
        'https://www.pure-bbw.com/',
        'https://www.pure-ts.com/',
        'https://www.tspov.com/',
    ]

    selector_map = {
        'title': '//div[contains(@class, "titlebox")]//h3/text()',
        'description': '//div[contains(@class, "aboutvideo")]//p/text()',
        'performers': '//ul[contains(@class, "featuredModels")]/li//span/text()',
        'date': '//div[contains(@class, "video_description")]//h4/text()',
        're_date': r'\b(\d{1,4}-\d{1,2}-\d{1,2})\b',
        'image': '//div[contains(@class, "videohere")]//img[contains(@src,"contentthumbs")]/@src',
        'tags': '//meta[@name="keywords"]/@content',
        'trailer': '//script[contains(text(),"playTrailer")]/text()',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/updates/page_%s.html',

    }

    def get_scenes(self, response):
        scenes = response.xpath('//body//section[2]//div[@class="empireimg"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = self.process_xpath(
            response, self.get_selector_map('tags')).get()
        if tags:
            tags = tags.split(",")
            return tags

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            return self.format_link(response, image)

        image = response.xpath('//script[contains(text(),"playTrailer")]/text()').get()
        if image:
            image = re.search(r'\simage:\ \"(.*?)\".', image).group(1)
            image = "https://www.pure-ts.com/" + image
            return self.format_link(response, image)
        return ''

    def get_trailer(self, response):
        trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search(r'\sfile:\ \"(.*?)\",', trailer).group(1)
            trailer = "https://www.pure-ts.com/" + trailer
            return self.format_link(response, trailer)
        return ''

    def get_site(self, response):
        if "becomingfemme" in response.url:
            return "Becoming Femme"
        if "pure-bbw" in response.url:
            return "Pure BBW"
        if "pure-ts" in response.url:
            return "Pure TS"
        if "tspov" in response.url:
            return "TSPOV"

    def get_gender(self, response):
        if "becomingfemme" in response.url:
            return "Female"
        return "Trans"
