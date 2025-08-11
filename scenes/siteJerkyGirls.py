import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteJerkyGirlsSpider(BaseSceneScraper):
    name = 'JerkyGirls'
    network = 'Jerky Girls'
    parent = 'Jerky Girls'
    site = 'Jerky Girls Official'

    start_urls = [
        'https://www.jerkygirls.com',
    ]

    selector_map = {
        'title': '//h4//text()',
        'description': '//div[contains(@class, "vidImgContent")]//text()',
        'date': '//i[contains(@class, "calendar")]/../following-sibling::text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[contains(@class, "VOD_update")]/img/@src0_4x',
        'performers': '//div[contains(@class, "gallery_info")]//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="blogTags"]/ul/li/a/text()',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="latestUpdateB"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-setid').get()
            scene = scene.xpath('./div[1]/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//i[contains(@class, "fa-video")]/following-sibling::text()[contains(., "min")]')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Jerky Girls"
                perf['site'] = "Jerky Girls Official"
                performers_data.append(perf)
        return performers_data
