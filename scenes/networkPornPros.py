import re
import dateparser
import scrapy
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper


class PornprosSpider(BaseSceneScraper):
    name = 'PornPros'
    network = 'pornpros'

    start_urls = [
        "https://anal4k.com",
        "https://baeb.com",
        "https://bbcpie.com",
        "https://castingcouch-x.com",
        "https://cum4k.com",
        "https://exotic4k.com",
        "https://facials4k.com",
        "https://fantasyhd.com",
        "https://girlcum.com",
        "https://holed.com",
        "https://lubed.com",
        "https://myveryfirsttime.com",
        "https://nannyspy.com",
        "https://passion-hd.com",
        "https://pornpros.com",
        "https://povd.com",
        "https://puremature.com",
        "https://spyfam.com",
        'https://tiny4k.com',
        'https://wetvr.com',
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="dvdTitle"]/text() | //h1[contains(@class, "t2019-stitle")]/text() | //div[contains(@class, "scene-info")]//h1/text()',
        'description': '//div[@class="sceneDesc bioToRight showMore"]/text() | //div[@class="sceneDescText"]/text() | //p[@class="sceneDesc showMore"]/text() | //p[@class="descriptionText"]/text() | //div[@id="t2019-description"]/text() | //i[contains(@class, "fa-quote-right")]/../span/text()',
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text() | //div[@id="t2019-stime"]//span/text()',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //div[@class="sceneCol scenePerformers"]//a/text() | //div[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoPerformerCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerPerformerCarousel"]//a/text() | //div[@id="t2019-models"]/a/text() | //span[contains(text(),"Featuring")]/../a/text()',
        'tags': '//div[@class="sceneCol sceneColCategories"]//a/text() | //div[@class="sceneCategories"]//a/text() | //p[@class="dvdCol"]/a/text()',
        'duration': '//div[contains(@id, "stime")]/div/span[contains(text(), "minutes")]/text()',
        're_duration': r'(\d+)',
        'external_id': r'video/(.+)',
        'trailer': '//video//source/@src',
        'pagination': '/?page=%s'
    }

    max_pages = 100

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count or "pornpros" in response.url:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath("//div[contains(@class, 'items-center')]//nav/..//div[@data-vid]")

        # In case a site is added that uses the old layout
        if len(scenes) == 0:
            scenes = response.xpath("//div[contains(@class, 'video-releases-list')]//div[@data-video-id]")

        for scene in scenes:
            link = self.format_link(response, scene.css('a::attr(href)').get())

            # if link = /join we can guesstimate by using the title and slugifying
            if link == self.format_link(response, "/join"):
                link = self.format_link(response, "/video/" + slugify(scene.xpath(".//a[contains(@class, 'title')]/text()").get()))

            meta = {}

            parsescene = True
            if "pornpros" in response.url:
                link = self.format_link(response, scene.xpath('.//a[contains(@class,"title")]/@href').get())
                sceneid = re.search(r'video/(.+)', link).group(1).strip()
                with open('dupelist-pornpros.txt', 'r', encoding="utf-8") as file1:
                    for i in file1.readlines():
                        if sceneid in i:
                            parsescene = False
                            break

            if scene.css('div::attr(data-date)').get() is not None:
                meta['date'] = dateparser.parse(
                    scene.css('div::attr(data-date)').get()).isoformat()
            elif scene.xpath('.//div[contains(@class, "video-thumbnail-footer")]//span[contains(@class, "text-xs")]/text()').get() is not None:
                meta['date'] = dateparser.parse(
                    scene.xpath('.//div[contains(@class, "video-thumbnail-footer")]//span[contains(@class, "text-xs")]/text()').get()).isoformat()

            if parsescene:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = None
        if "wetvr" in response.url:
            image = response.xpath('//dl8-video/@poster').get()

        if response.xpath('//meta[@name="twitter:image"]').get() is not None:
            image = response.xpath('//meta[@name="twitter:image"]/@content').get()

        if not image:
            if response.xpath('//video').get() is not None:
                if response.xpath('//video/@poster').get() is not None:
                    image = response.xpath('//video/@poster').get()
        if not image:
            if response.xpath('//img[@id="no-player-image"]') is not None:
                image = response.xpath('//img[@id="no-player-image"]/@src').get()

        if image:
            if "?imgw" in image:
                image = re.search(r'(.*)\?imgw', image).group(1)
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        if "validfrom" not in trailer:
            return trailer
        return None

    def get_duration(self, response):
        duration = super().get_duration(response)
        if len(duration) > 3:
            seconds = "." + duration[2:]
            minutes = duration[:2]
            duration = str(round((int(minutes) * 60) + (float(seconds) * 60)))
        elif duration:
            duration = str(int(duration) * 60)
        return duration
