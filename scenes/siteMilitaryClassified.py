import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMilitaryClassifiedSpider(BaseSceneScraper):
    name = 'MilitaryClassified'
    site = 'MilitaryClassified'
    parent = 'MilitaryClassified'
    network = 'MilitaryClassified'

    start_urls = [
        'https://militaryclassified.com'
    ]

    selector_map = {
        'description': '',
        'date': '',
        'image': '//video/@poster',
        'performers': '',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/dt/classic/Nav/ByRelease%s.html',
    }

    def get_next_page_url(self, base, page):
        url = f"https://militaryclassified.com/dt/classic/Nav/ByRelease{page:03}.html"
        return url

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="RecruitBox"]')
        for scene in scenes:
            title = scene.xpath('.//div[@class="RecruitBoxText"]/text()')
            if title:
                meta['title'] = string.capwords(title.get())
            scene = scene.xpath('./../@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Gay', 'Military']

    def get_id(self, response):
        sceneid = super().get_id(response)
        return sceneid.lower()
