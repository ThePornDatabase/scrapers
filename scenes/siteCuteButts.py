import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCuteButtsSpider(BaseSceneScraper):
    name = 'CuteButts'
    network = 'Tsunami Cash'
    parent = 'CuteButts'
    site = 'CuteButts'

    start_urls = [
        'https://www.cutebutts.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '',
        'image': '//div[@class="vid"]/div[contains(@class, "player")]/@style',
        're_image': r'(http.*?)\)',
        'performers': '//h4[@class="model"]/a/text()',
        'tags': '//a[@class="tag"]/text()',
        'trailer': '',
        'external_id': r'sample/(.*?)/',
        'pagination': '/samples?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scene"]//a[@class="id"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        datetext = response.xpath('//strong[contains(text(), "Date:")]/following-sibling::text()')
        if datetext:
            datetext = datetext.get()
            datetext = re.search(r'(\d{4}).*?(\d{2}).*?(\d{2})', datetext)
            if datetext:
                return datetext.group(1) + "-" + datetext.group(2) + "-" + datetext.group(3)
        return ""

    def get_duration(self, response):
        duration = response.xpath('//strong[contains(text(), "Runtime:")]/following-sibling::text()[1]')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "Tsunami Cash"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data
