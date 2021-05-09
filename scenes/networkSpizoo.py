import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SpizooSpider(BaseSceneScraper):
    name = 'Spizoo'
    network = "Spizoo"
    parent = "Spizoo"

    start_urls = [
        'https://firstclasspov.com/',
        'https://mrluckypov.com/',
        'https://rawattack.com/',
        'https://realsensual.com/',
        'https://www.spizoo.com',
    ]

    selector_map = {
        'title': '/',
        'description': '',
        'date': "//p[@class='date']/text()",
        'image': '',  # Hashed and tokened link.  Will be no good later
        'performers': '',
        'tags': "",
        'external_id': '\\/updates\\/(.*)\\.html$',
        'trailer': '',  # Hashed and tokened link.  Will be no good later
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//a[@data-event='106']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        if "spizoo" in response.request.url:
            titlexpath = '//div[@class="title"]/h1/text()'
        matches = ["firstclasspov", "mrluckypov"]
        if any(x in response.request.url for x in matches):
            titlexpath = '//section[@id="scene"]/div/div/div/h1/text()'
        if "rawattack" in response.request.url:
            titlexpath = '//title/text()'
        if "realsensual" in response.request.url:
            titlexpath = '//h2[contains(@class,"titular")]/text()'
        return response.xpath(titlexpath).get().strip()

    def get_tags(self, response):
        if "spizoo" in response.request.url:
            tagsxpath = '//a[contains(@class,"category-tag")]/@title'
        else:
            tagsxpath = '//a[contains(@href,"/categories/")]/text()'

        tags = response.xpath(tagsxpath).getall()
        return list(map(lambda x: x.strip(), tags))

    def get_performers(self, response):
        matches = ["firstclasspov", "rawattack"]
        if any(x in response.request.url for x in matches):
            performersxpath = '//div[@class="col-12"]//a[contains(@href, "/models")]/@title'
        matches = ["mrluckypov", "realsensual", "spizoo"]
        if any(x in response.request.url for x in matches):
            performersxpath = '//div[@class="col-3"]//a[contains(@href, "/models")]/@title'

        tags = response.xpath(performersxpath).getall()
        return list(map(lambda x: x.strip(), tags))

    def get_image(self, response):
        if "rawattack" in response.request.url:
            imagexpath = '//div[@id="hpromo"]/a/img[contains(@src,".jpg")]/@src'
        else:
            imagexpath = '//video/@poster'
        return response.xpath(imagexpath).get().strip()

    def get_trailer(self, response):
        if "rawattack" in response.request.url:
            trailerxpath = '//video[@id="trailervideo"]/source/@src'
        else:
            trailerxpath = '//video/source/@src'
        return response.xpath(trailerxpath).get().strip()

    def get_description(self, response):
        if "rawattack" in response.request.url:
            descriptionxpath = '//section[@id="sceneInfo"]/div/div/div/p/text()'
        elif "realsensual" in response.request.url:
            descriptionxpath = '//p[@class="description-scene"]/text()'
        else:
            descriptionxpath = '//p[@class="description"]/text()'
        return response.xpath(descriptionxpath).get().strip()
