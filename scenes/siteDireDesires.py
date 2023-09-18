import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDireDesiresSpider(BaseSceneScraper):
    name = 'DireDesires'
    network = 'Dire Desires'
    parent = 'Dire Desires'
    site = 'Dire Desires'

    start_urls = [
        'https://diredesires.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@itemprop="articleBody"]//text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class, "entry-byline")]//strong/text()',
        'tags': '',
        'duration': '//span[@class="axm-video-duration"]/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@id="primary"]//article')
        for scene in scenes:
            scenedate = scene.xpath('.//time[contains(@class, "entry-date")]/@datetime')
            if scenedate:
                scenedate = scenedate.get()
                meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)
            duration = scene.xpath('.//span[@class="axm-video-duration"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration).group(1)
                meta['duration'] = self.duration_to_seconds(duration)
            scene = scene.xpath('.//h3/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers_orig = super().get_performers(response)
        performers = []
        for performer in performers_orig:
            if "diredesires" not in performer.lower():
                performers.append(performer)
        return performers
