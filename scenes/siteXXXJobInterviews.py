import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXXXJobInterviewsSpider(BaseSceneScraper):
    name = 'XXXJobInterviews'
    network = 'XXX Job Interviews'
    parent = 'XXX Job Interviews'
    site = 'XXX Job Interviews'

    start_urls = [
        'https://xxxjobinterviews.com',
    ]

    selector_map = {
        'title': '//div[@class="video-description"]/div[1]/text()',
        'description': '//div[contains(@class,"description")]/span/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="profile-item"]//a/text()',
        'tags': '//div[@class="tags"]/ul/li/a/text()',
        'duration': '//div[@class="video-description"]//span[contains(text(), "Runtime")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'.*-(\d+)\.htm',
        'pagination': '/videos/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="gallery-item"]')
        for scene in scenes:
            duration = scene.xpath('.//div[contains(@class, "info-container")]/div/span[1]/text()')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(duration.strip())
            scenedate = scene.xpath('.//div[contains(@class, "info-container")]/div/span[2]/text()')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = scenedate.strip()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = response.xpath('//div[@class="tags"]/ul/li/a/text()').getall()
        tags2 = []
        for tag in tags:
            if re.sub(r'[A-Z]', '', tag) == tag:
                tags2.append(string.capwords(tag))
        return tags2
