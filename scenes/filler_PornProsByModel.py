import re
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class FillerPornprosByModelSpider(BaseSceneScraper):
    name = 'PornProsByModel'
    network = 'pornpros'

    start_urls = [
        "https://pornpros.com/",
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="dvdTitle"]/text() | //h1[contains(@class, "t2019-stitle")]/text()',
        'description': '//div[@class="sceneDesc bioToRight showMore"]/text() | //div[@class="sceneDescText"]/text() | //p[@class="sceneDesc showMore"]/text() | //p[@class="descriptionText"]/text() | //div[@id="t2019-description"]/text()',
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text() | //div[@id="t2019-stime"]//span/text()',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //div[@class="sceneCol scenePerformers"]//a/text() | //div[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoPerformerCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerPerformerCarousel"]//a/text() | //div[@id="t2019-models"]/a/text()',
        'tags': '//div[@class="sceneCol sceneColCategories"]//a/text() | //div[@class="sceneCategories"]//a/text() | //p[@class="dvdCol"]/a/text()',
        'duration': '//div[contains(@id, "stime")]/div/span[contains(text(), "minutes")]/text()',
        're_duration': r'(\d+)',
        'external_id': r'video/(.+)',
        'trailer': '//video//source/@src',
        'pagination': '/girls?page=%s'
    }

    max_pages = 100

    def parse(self, response, **kwargs):
        scenes = self.get_models(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count or "pornpros" in response.url:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] < 500:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_models(self, response):
        meta = response.meta
        models = response.xpath('//div[@class="btn-group"]/a/@href').getall()
        for model in models:
            model = self.format_link(response, model)
            yield scrapy.Request(model, callback=self.get_scenes, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath("//h3/following-sibling::div/div")
        for scene in scenes:
            # ~ sceneurl = self.format_link(response, scene.xpath('./div/a/@href').get())
            parsescene = True
            # ~ sceneid = re.search(r'video/(.+)', sceneurl).group(1).strip()
            # ~ with open('pornpros-url-list.txt', 'r', encoding="utf-8") as file1:
                # ~ for i in file1.readlines():
                    # ~ if sceneurl in i:
                        # ~ parsescene = False
                        # ~ print (f"Skippineg: {sceneurl}")
                        # ~ break
            link = self.format_link(response, scene.xpath('.//div[@class="information"]/a/@href').get())
            sceneid = re.search(r'video/(.+)', link).group(1).strip()
            with open('dupelist-pornpros.txt', 'r', encoding="utf-8") as file1:
                for i in file1.readlines():
                    if sceneid in i:
                        parsescene = False
                        break

            if scene.xpath('./div/@data-date').get() is not None:
                meta['date'] = dateparser.parse(scene.xpath('./div/@data-date').get()).isoformat()

            # ~ if parsescene:
                # ~ yield scrapy.Request(sceneurl, callback=self.parse_scene, meta=meta)
            if parsescene:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = None
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
