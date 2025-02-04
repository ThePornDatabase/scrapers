import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteErotericSpider(BaseSceneScraper):
    name = 'Eroteric'
    network = 'Eroteric'
    parent = 'Eroteric'
    site = 'Eroteric'

    start_urls = [
        'https://www.eroteric.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//figure/following-sibling::p[1]//text()',
        'date': '//li[contains(@class, "meta-date")]/span/text()',
        'image': '//video/@poster',
        'performers': '//div[contains(@class, "bwp-post")]/a[contains(@href, "/tag/")]/text()',
        'tags': '',
        'duration': '//span[contains(@class, "updated") and contains(text(), "min")]/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article')
        for scene in scenes:
            meta['id'] = re.search(r'(\d+)', scene.xpath('./@id').get()).group(1)
            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//span[contains(@class, "updated") and contains(text(), "min")]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^0-9minsec]+', '', duration)
            minutes = re.search(r'(\d+)min', duration)
            seconds = re.search(r'(\d+)sec', duration)

            total = 0
            if minutes:
                total = total + (int(minutes.group(1)) * 60)
            if seconds:
                total = total + int(seconds.group(1))
            return str(total)
        return None
