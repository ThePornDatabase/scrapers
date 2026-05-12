import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDezyredSpider(BaseSceneScraper):
    name = 'Dezyred'
    network = 'Dezyred'
    parent = 'Dezyred'
    site = 'Dezyred'

    start_urls = [
        'https://dezyred.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[contains(@class,"full-width text-dezyred-white")]/div/text()',
        'image': '//div[@class="image-wrapper poster"]/img/@src',
        'performers': '//div[@class="Page_grid__RDdDE"]/a/div[contains(@class,"StarCard_name")]/text()',
        'external_id': r'',
        'pagination': '/games?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="GameCard"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@playagameid').get().lower()
            if "." in meta['id']:
                meta['id'] = re.search(r'\.(.*)', meta['id']).group(1)

            scenedate = scene.xpath('./@createdat').get()
            if scenedate:
                meta['date'] = self.parse_date(scenedate.strip()).strftime('%Y-%m-%d')

            sceneurl = scene.xpath('./div[contains(@class, "image-container")]/a/@href').get()

            if meta['id'] and sceneurl and self.check_item(meta, self.days) and sceneurl not in response.url:
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_tags(self,response):
        return ['Virtual Reality', 'VR']

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Dezyred"
                perf['site'] = "Dezyred"
                performers_data.append(perf)
        return performers_data
    