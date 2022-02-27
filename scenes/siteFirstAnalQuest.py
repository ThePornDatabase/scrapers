import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFirstAnalQuestSpider(BaseSceneScraper):
    name = 'FirstAnalQuest'
    network = 'First Anal Quest'
    parent = 'First Anal Quest'
    site = 'First Anal Quest'

    start_urls = [
        'http://www.firstanalquest.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[@class="text-desc"]/p/text()',
        'date': '',
        'image': '//img[@class="player-preview"]/@src',
        'performers': '//ul[contains(text(), "Models")]/li/a/text()',
        'tags': '//ul[@class="list-inline"]/li/a[contains(@href, "/tags/")]/text()',
        'external_id': r'.*-(\d+)/$',
        'trailer': '//script[contains(text(), "flashvars")]/text()',
        're_trailer': r'flashvars.*?(http.*?\.mp4)',
        'pagination': '/latest-updates/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb-content"]')
        for scene in scenes:
            meta = {}
            date = scene.xpath('./div/span[@class="thumb-added"]/text()')
            if date:
                meta['date'] = self.parse_date(date.get(), date_formats=['%b %d, %Y']).isoformat()
            else:
                meta['date'] = self.parse_date('today').isoformat()
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
