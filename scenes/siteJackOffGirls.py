import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJackOffGirlsSpider(BaseSceneScraper):
    name = 'JackOffGirls'
    site = 'Jack Off Girls'
    parent = 'Jack Off Girls'
    network = 'Jack Off Girls'

    start_urls = [
        'https://jackoffgirls.com'
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '//div[contains(@class,"videoDetails")]/p//text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//li[contains(text(), "Tags:")]/following-sibling::li/a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=[\'\"](.*?)[\'\"]',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/Movies/%s/latest/',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "item-thumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"videoInfo")]/p/text()[contains(., "of video")]')
        if duration:
            duration = re.sub(r'[^a-z0-9]', "", duration.get().replace("&nbsp;", "").lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()

    def get_title(self, response):
        title = super().get_title(response)
        if not title:
            title = re.search(r'.*/(.*?)\.htm', response.url).group(1)
            title = string.capwords(title.replace("-", " ").replace("_", " "))
        return title
