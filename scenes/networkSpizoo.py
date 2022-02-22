import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'firstclasspov': "First Class POV",
        'mrluckypov': "Mr Lucky POV",
        'mrluckyraw': "Mr Lucky Raw",
        'mrluckyvip': "Mr Lucky VIP",
        'rawattack': "Raw Attack",
        'realsensual': "Real Sensual",
        'spizoo': "Spizoo",
    }
    return match.get(argument, argument)


class SpizooSpider(BaseSceneScraper):
    name = 'Spizoo'
    network = "Spizoo"

    start_urls = [
        'https://firstclasspov.com/',
        'https://mrluckypov.com/',
        'https://mrluckyraw.com/',
        'https://mrluckyvip.com/',
        'https://rawattack.com/',
        'https://realsensual.com/',
        'https://www.spizoo.com/',
    ]

    selector_map = {
        'title': '/',
        'description': '',
        'date': "//p[@class='date']/text()",
        'image': '//video/@poster|//div[@id="hpromo"]/a/img[contains(@src,".jpg")]/@src',
        'performers': '//div[@class="col-12"]//a[contains(@href, "/models")]/@title|//div[@class="col-3"]//a[contains(@href, "/models")]/@title',
        'tags': '//a[contains(@class,"category-tag")]/@title|//a[contains(@href,"/categories/")]/text()',
        'external_id': r'/updates/(.*)\.html$',
        'trailer': '',  # Hashed and tokened link.  Will be no good later
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        if "mrluckyvip" in response.url:
            scenes = response.xpath('//div[@class="thumb-pic"]/a/@href').getall()
        elif "mrluckyraw" in response.url:
            scenes = response.xpath("//div[@class='thumb-title']/a/@href").getall()
        else:
            scenes = response.xpath("//a[@data-event='106']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        matches = ["spizoo", "mrluckyraw", "mrluckyvip"]
        if any(x in response.url for x in matches):
            titlexpath = '//div[@class="title"]/h1/text()'
        matches = ["firstclasspov", "mrluckypov"]
        if any(x in response.url for x in matches):
            titlexpath = '//section[@id="scene"]/div/div/div/h1/text()'
        if "rawattack" in response.url:
            titlexpath = '//title/text()'
        if "realsensual" in response.url:
            titlexpath = '//h2[contains(@class,"titular")]/text()'
        return response.xpath(titlexpath).get().strip()

    def get_description(self, response):
        if "rawattack" in response.url:
            descriptionxpath = '//section[@id="sceneInfo"]/div/div/div/p/text()'
        elif "realsensual" in response.url:
            descriptionxpath = '//p[@class="description-scene"]/text()'
        else:
            descriptionxpath = '//p[@class="description"]/text()'
        return response.xpath(descriptionxpath).get().strip()

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_next_page_url(self, base, page):
        if page == 1:
            return base + 'categories/Movies.html'
        return self.format_url(base, self.get_selector_map('pagination') % page)
