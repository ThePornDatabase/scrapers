import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFancySteelSpider(BaseSceneScraper):
    name = 'FancySteel'
    network = 'FancySteel'
    parent = 'FancySteel'
    site = 'FancySteel'

    start_urls = [
        'https://fancysteel.com',
    ]

    selector_map = {
        'title': '//script[@id="viewed_product"]/text()',
        're_title': r'Name: [\"](.*?)[\"]',
        'description': '//div[@class="product-block"]//div/span/text()',
        'date': '//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "release date:")]/../following-sibling::div[1]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'trailer': '',
        'external_id': r'',
        'pagination': '/collections/videodownloads?page=%s',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 4,
        # ~ 'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "grid__item")]//button/following-sibling::a[contains(@href, "/videodownloads/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        sceneid = response.xpath('//script[@id="viewed_product"]/text()').get()
        sceneid = re.search(r'ProductID: (\d+)', sceneid).group(1)
        return sceneid

    def get_duration(self, response):
        duration = response.xpath('//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "runtime:")]/../following-sibling::div[1]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
            return duration

    def get_tags(self, response):
        tags = response.xpath('//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "fetishes:")]/following-sibling::div[@class="meta-value"][1]//text()')
        scene_tags = []
        if tags:
            tags = tags.get()
            tags = tags.lower()
            tags = tags.strip(string.punctuation).strip()
            tags = tags.replace(" and ", "")
            if "," in tags:
                tags = tags.split(",")
                for tag in tags:
                    scene_tags.append(string.capwords(tag.strip()))
        return scene_tags

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "meta-title") and contains(text(), "Starring")]/following-sibling::div[contains(@class, "meta-value")][1]//span/text()')
        scene_performers = []
        if performers:
            performers = performers.get()
            performers = performers.strip(string.punctuation).strip()
            if "," in performers:
                performers = performers.split(",")
                for performer in performers:
                    scene_performers.append(string.capwords(performer.strip()))
        return scene_performers

    def get_date(self, response):
        scenedate = response.xpath('//label[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "release date:")]/../following-sibling::div[1]/text()')
        scene_date = ""
        if scenedate:
            scenedate = scenedate.get()
            try:
                scene_date = self.parse_date(scenedate).strftime('%Y-%m-%d')
            except:
                scene_date = ""
        return scene_date

    def get_title(self, response):
        title = super().get_title(response)
        if len(title) < 3:
            title = title + "."
        return title
