import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkNookiesSpider(BaseSceneScraper):
    name = 'Nookies'
    network = 'Nookies'

    start_urls = [
        'https://nookies.com',
    ]

    selector_map = {
        'title': '//div[@class="video-box"]/h1/text()|//div[contains(@class,"video-content")]/h1/text()',
        'description': '//comment()[contains(., "Description")]/following-sibling::div[1]/p[not(contains(text(), "Description:"))]//text()',
        'performers': '//comment()[contains(., "Models")]/following-sibling::div[1]/a/span/text()',
        'tags': '//a[@class="pill-link" and contains(@href, "/tag/")]/text()',
        'duration': '//h3/following-sibling::p//i[contains(@class, "fa-video")]/following-sibling::text()[contains(., ":")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '//div[@class="video-box"]/div[@class="player"]//source/@src',
        'external_id': r'.*/(.*)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="video-card-text"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="date"]/text()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = scenedate.group(1)
            scene = scene.xpath('./h4/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and self.check_item(meta, self.days):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//comment()[contains(., "Site")]/following-sibling::div[1]/a/span/text()|//a[contains(@class, "btn-site")]/img/@alt')
        if site:
            site = site.get()
            return site.strip()
        else:
            return "Nookies"

    def get_parent(self, response):
        parent = response.xpath('//comment()[contains(., "Site")]/following-sibling::div[1]/a/span/text()|//a[contains(@class, "btn-site")]/img/@alt')
        if parent:
            parent = parent.get()
            return parent.strip()
        else:
            return "Nookies"

    def get_image(self, response):
        image = response.xpath('//div[contains(@id, "trailer")]/div[contains(@class, "responsive")]/img/@src')
        if not image:
            image = response.xpath('//div[@class="video-box"]/div[@class="player"]/div[@class="responsive-image"]/img/@src')
            if not image:
                image = response.xpath('//script[contains(text(), "fluidPlayer")]/text()')
                if image:
                    image = re.search(r'posterImage.*?(http.*?)[\'\"]', image.get())
                    if image:
                        image = image.group(1)
        if image:
            image = image.get()
        if image:
            image = image.replace(" ", "%20")
        return image
    
    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Nookies"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data
