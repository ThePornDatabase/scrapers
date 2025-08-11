import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXesPLSpider(BaseSceneScraper):
    name = 'XesPL'
    network = 'Xes.PL'
    parent = 'Xes.PL'
    site = 'Xes.PL'

    start_urls = [
        'https://xes.pl',
    ]

    cookies = [{"name": "lang_select", "value": "eng"}]

    selector_map = {
        'title': '//h1//text()',
        'description': '//article/p/text()',
        'date': '//td[contains(text(), "Add date")]/following-sibling::td/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//td[contains(text(), "Actors")]/following-sibling::td/ul/li/a/text()',
        'tags': '//td[contains(text(), "Categories")]/following-sibling::td/ul/li/a/text()',
        'duration': '//td[contains(text(), "Duration")]/following-sibling::td/text()',
        'trailer': '',
        'external_id': r',(\d+),',
        'pagination': '/katalog_filmow,%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="big-box-video"]//h2/a[contains(@href, "epizod")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None

    def get_title(self, response):
        title = response.xpath('//h1//text()')
        if title:
            title = title.getall()
            title = self.cleanup_title("".join(title))
            return title
        return ""
