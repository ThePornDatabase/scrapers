import re
import html
import json
import requests
import string
import unidecode
import scrapy
from scrapy import Selector
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMFVideoXXXSpider(BaseSceneScraper):
    name = 'MFVideoXXX'
    site = 'MF Video'
    network = 'MF Video'
    parent = 'MF Video'

    start_urls = [
        'https://www.mfvideoxxx.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="entry-content"]/p[not(script)]//text()',
        'image': '//video/@poster',
        'performers': '//h6[contains(text(), "Models")]/a/text()',
        'tags': '',
        'external_id': r'',
        'pagination': '/new-videos/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//article')
        for scene in scenes:
            scenedate = scene.xpath('.//time[contains(@class, "published")]/@datetime').get()
            if scenedate:
                meta['date'] = self.parse_date(scenedate).strftime('%Y-%m-%d')
            
            sceneitem = scene.xpath('./@id').get()
            if sceneitem:
                meta['id'] = re.search(r'post-(\d+)', sceneitem).group(1)

            scene = scene.xpath('./div[1]/a/@href').get()

            if meta['id'] and self.check_item(meta, self.days):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="column2"]//b[contains(text(), "inutes")]/text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return ""

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                return image.get()
            else:
                return ""
        return image

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "MF Video"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)

        return performers_data
    