import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGot2PeeSpider(BaseSceneScraper):
    name = 'Got2Pee'
    network = 'Puffy Network'
    parent = 'Got2Pee'
    site = 'Got2Pee'

    start_urls = [
        'https://got2pee.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="movie-description"]/text()',
        'date': '',
        'image': '//img[@class="videoplayer-img"]/@src',
        'performers': '',
        'tags': '//span[@class="tags-list"]/a/text()',
        'external_id': r'videos/(.*?)/',
        'trailer': '',
        'pagination': '/videos/page-%s/?tag=&site=&model=&sort=recent&pussy='
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video-frame"]')
        for scene in scenes:
            date = scene.xpath('.//span[@class="views left"]/text()')
            if date:
                meta['date'] = self.parse_date(date.get(), date_formats=['%b %d, %Y']).isoformat()
            else:
                meta['date'] = self.format_date('today').isoformat()

            scene = scene.xpath('.//a[@class="kt_imgrc"]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags = list(map(lambda x: string.capwords(x.replace("#", "").strip()), tags))
        return tags
