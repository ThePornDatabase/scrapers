import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkNookiesSpider(BaseSceneScraper):
    name = 'Nookies'
    network = 'Nookies'

    start_urls = [
        'https://nookies.com',
    ]

    selector_map = {
        'title': '//div[@class="video-box"]/h1/text()',
        'description': '//div[contains(@class,"video-content")]/h6/following-sibling::p//text()',
        'date': '',
        'performers': '//div[@class="tags"]/a[contains(@href, "/model/")]/span/text()',
        'tags': '',
        'duration': '',
        'trailer': '//div[@class="video-box"]/div[@class="player"]//source/@src',
        'external_id': r'.*/(.*)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-card-text"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="date"]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = scenedate.group(1)
            scene = scene.xpath('./h4/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[@class="tags"]/a[contains(@href, "/site/")]/span/text()')
        if site:
            site = site.get()
            return site.strip()
        else:
            return "Nookies"

    def get_parent(self, response):
        parent = response.xpath('//div[@class="tags"]/a[contains(@href, "/site/")]/span/text()')
        if parent:
            parent = parent.get()
            return parent.strip()
        else:
            return "Nookies"

    def get_image(self, response):
        image = response.xpath('//div[@class="video-box"]/div[@class="player"]/div[@class="responsive-image"]/img/@src')
        if not image:
            image = response.xpath('//script[contains(text(), "fluidPlayer")]/text()')
            if image:
                image = re.search(r'posterImage.*?(http.*?)[\'\"]', image.get())
                if image:
                    image = image.group(1)
        else:
            image = image.get()
        image = image.replace(" ", "%20")
        return image
