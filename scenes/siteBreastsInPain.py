import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBreastsInPainSpider(BaseSceneScraper):
    name = 'BreastsInPain'
    site = 'BreastsInPain'
    parent = 'BreastsInPain'
    network = 'BreastsInPain'

    start_urls = [
        'https://www.breastsinpain.com',
    ]

    selector_map = {
        'title': '//h4[@class="post-title"]/text()',
        'description': '//div[contains(@class,"post-excerpt")]/p/text()',
        'date': '//time[@class="entry-date"]/@datetime',
        'image': '//a[@rel="prettyPhoto"]/img/@src',
        'performers': '//text()[contains(., "Models:")]/following-sibling::a/text()',
        'tags': '//a[@rel="category tag"]/text()',
        'duration': '//div[contains(@class,"meta-trio")]/text()[contains(., "mins")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'external_id': r'.*/(.*?)/',
        'pagination': '/updatespage/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h4[@class="post-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("BDSM")
        tags.append("Bondage")
        tags.append("Fetish")
        return tags

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = self.get_network(response)
                perf['site'] = self.get_network(response)
                performers_data.append(perf)
        return performers_data

    def get_id(self, response):
        sceneid = response.xpath('//div[@class="post-meta-trio"]/text()[1]').get()
        sceneid = sceneid.strip()
        sceneid = re.search(r'^(.*?)\|', sceneid).group(1)

        return sceneid.lower().strip()
