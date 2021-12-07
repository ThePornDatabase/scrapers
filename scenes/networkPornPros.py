from tpdb.BaseSceneScraper import BaseSceneScraper
import dateparser
import scrapy
from slugify import slugify


class PornprosSpider(BaseSceneScraper):
    name = 'PornPros'
    network = 'pornpros'

    start_urls = [
        "https://anal4k.com/",
        "https://baeb.com/",
        "https://bbcpie.com/",
        "https://castingcouch-x.com/",
        "https://cum4k.com/",
        "https://exotic4k.com/",
        "https://facials4k.com/",
        "https://fantasyhd.com/",
        "https://girlcum.com/",
        "https://holed.com/",
        "https://lubed.com/",
        "https://myveryfirsttime.com/",
        "https://nannyspy.com/"
        "https://passion-hd.com/",
        "https://pornpros.com/",
        "https://povd.com/",
        "https://puremature.com/",
        "https://spyfam.com/",
        'https://tiny4k.com/',
        'https://wetvr.com/',
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="dvdTitle"]/text() | //h1[contains(@class, "t2019-stitle")]/text()',
        'description': '//div[@class="sceneDesc bioToRight showMore"]/text() | //div[@class="sceneDescText"]/text() | //p[@class="sceneDesc showMore"]/text() | //p[@class="descriptionText"]/text() | //div[@id="t2019-description"]/text()',
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text() | //div[@id="t2019-stime"]//span/text()',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //div[@class="sceneCol scenePerformers"]//a/text() | //div[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoPerformerCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerPerformerCarousel"]//a/text() | //div[@id="t2019-models"]/a/text()',
        'tags': '//div[@class="sceneCol sceneColCategories"]//a/text() | //div[@class="sceneCategories"]//a/text() | //p[@class="dvdCol"]/a/text()',
        'external_id': 'video\\/(.+)',
        'trailer': '//video//source/@src',
        'pagination': '/?page=%s'
    }

    max_pages = 100

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'video-releases-list')]//div[@data-video-id]")
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {}

            if scene.css('div::attr(data-date)').get() is not None:
                meta['date'] = dateparser.parse(
                    scene.css('div::attr(data-date)').get()).isoformat()

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        if response.xpath('//meta[@name="twitter:image"]').get() is not None:
            return response.xpath(
                '//meta[@name="twitter:image"]/@content').get()

        if response.xpath('//video').get() is not None:
            if response.xpath('//video/@poster').get() is not None:
                return response.xpath('//video/@poster').get()

        if response.xpath('//img[@id="no-player-image"]') is not None:
            return response.xpath('//img[@id="no-player-image"]/@src').get()
