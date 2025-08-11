import re
import scrapy
from scrapy.http import TextResponse
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLoveHomePornSpider(BaseSceneScraper):
    name = 'LoveHomePorn'
    network = 'Love Home Porn'
    parent = 'Love Home Porn'
    site = 'Love Home Porn'

    start_urls = [
        'https://lovehomeporn.com',
    ]

    selector_map = {
        'title': '//h1[@itemprop="description"]/text()',
        'description': '//div[contains(@class, "video-seo_text")]/text()',
        'date': '//div[@class="block-bg default"]/div[1]/div[1]/div[1]/meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//span[contains(text(), "Categories:")]/following-sibling::div[1]/a/text()',
        'duration': '//div[@class="column second"]//div[@class="item"]/i[contains(@class, "time")]/following-sibling::span/text()',
        'trailer': '',
        'external_id': r'video/(\d+)/',
        'pagination': '/videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="item-thumb"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        sanitized_html = response.text.replace('""', '"')
        sanitized_response = TextResponse(url=response.url, body=sanitized_html, encoding='utf-8')
        scenedate = super().get_date(sanitized_response)
        return scenedate
