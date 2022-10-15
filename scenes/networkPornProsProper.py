import os.path
import re
from pathlib import Path
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class PornprosSpider(BaseSceneScraper):
    name = 'PornProsProper'
    network = 'Porn Pros'

    start_url = "https://pornpros.com/"

    paginations = [
        ['/site/18yearsold?page=%s', '18 Years Old'],
        ['/site/40ozbounce?page=%s', '40oz Bounce'],
        ['/site/cockcompetition?page=%s', 'Cock Competition'],
        ['/site/crueltyparty?page=%s', 'Cruelty Party'],
        ['/site/cumshotsurprise?page=%s', 'Cumshot Surprise'],
        ['/site/deepthroatlove?page=%s', 'Deepthroat Love'],
        ['/site/disgraced18?page=%s', 'Disgraced 18'],
        ['/site/eurohumpers?page=%s', 'Euro Humpers'],
        ['/site/flexiblepositions?page=%s', 'Flexible Positions'],
        ['/site/freaksofboobs?page=%s', 'Freaks of Boob'],
        ['/site/freaksofcock?page=%s', 'Freaks of Cock'],
        ['/site/jurassiccock?page=%s', 'Jurassic Cock'],
        ['/site/massagecreep?page=%s', 'Massage Creep'],
        ['/site/pimpparade?page=%s', 'Pimp Parade'],
        ['/site/publicviolations?page=%s', 'Public Violations'],
        ['/site/realexgirlfriends?page=%s', 'Real Ex Girlfriends'],
        ['/site/shadypi?page=%s', 'Shady Pi'],
        ['/site/squirtdisgrace?page=%s', 'Squirt Disgrace'],
        ['/site/teenbff?page=%s', 'Teen BFF'],
    ]

    selector_map = {
        'title': '//h1[@class="sceneTitle"]/text() | //h3[@class="dvdTitle"]/text() | //h1[contains(@class, "t2019-stitle")]/text()',
        'description': '//div[@class="sceneDesc bioToRight showMore"]/text() | //div[@class="sceneDescText"]/text() | //p[@class="sceneDesc showMore"]/text() | //p[@class="descriptionText"]/text() | //div[@id="t2019-description"]/text()',
        'date': '//div[@class="tlcSpecs"]/span[@class="tlcSpecsDate"]/span[@class="tlcDetailsValue"]/text() | //*[@class="updatedDate"]/text() | //div[@id="t2019-stime"]//span/text()',
        'performers': '//div[@class="sceneCol sceneColActors"]//a/text() | //div[@class="sceneCol scenePerformers"]//a/text() | //div[@class="pornstarName"]/text() | //div[@id="slick_DVDInfoPerformerCarousel"]//a/text() | //div[@id="slick_sceneInfoPlayerPerformerCarousel"]//a/text() | //div[@id="t2019-models"]/a/text()',
        'tags': '//div[@class="sceneCol sceneColCategories"]//a/text() | //div[@class="sceneCategories"]//a/text() | //p[@class="dvdCol"]/a/text()',
        'duration': '//div[contains(@id, "stime")]/div/span[contains(text(), "minutes")]/text()',
        're_duration': r'(\d+)',
        'external_id': 'video\\/(.+)',
        'trailer': '//video//source/@src',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        for link in self.paginations:
            pagination = link[0]
            url = self.get_next_page_url(self.start_url, self.page, pagination)
            yield scrapy.Request(url, callback=self.parse,
                                 meta={'page': self.page, 'site': link[1], 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class,"site-list py-2")]//div[contains(@class, "video-releases-list")]//div[@data-video-id]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = response.meta

            if scene.css('div::attr(data-date)').get() is not None:
                meta['date'] = dateparser.parse(
                    scene.css('div::attr(data-date)').get()).isoformat()

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = None
        if response.xpath('//meta[@name="twitter:image"]').get() is not None:
            image =  response.xpath('//meta[@name="twitter:image"]/@content').get()

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
        if not "validfrom" in trailer:
            return trailer
        return None

    def get_site(self, response):
        meta = response.meta
        return meta['site']

    def get_parent(self, response):
        meta = response.meta
        return meta['site']

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        item['image'] = self.get_image(response)
        if 'image' not in item or not item['image']:
            item['image'] = None
        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        if 'image_blob' not in item:
            item['image_blob'] = None
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['duration'] = self.get_duration(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_network(response)
        item['type'] = 'Scene'

        if not os.path.exists('dupelist-pornpros.txt'):
            Path('dupelist-pornpros.txt').touch()
        with open('dupelist-pornpros.txt', 'a', encoding="utf-8") as file1:
            file1.write(item['id'] + "\n")

        yield self.check_item(item, self.days)

    def get_duration(self, response):
        duration = super().get_duration(response)
        if len(duration) > 3:
            seconds = "." + duration[2:]
            minutes = duration[:2]
            duration = str(round((int(minutes) * 60) + (float(seconds) * 60)))
        elif duration:
            duration = str(int(duration) * 60)
        return duration
