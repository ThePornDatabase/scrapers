import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkOldNannSpider(BaseSceneScraper):
    name = 'OldNanny'
    network = 'Old Nanny Network'

    start_urls = [
        'https://oldnanny.com',
    ]

    selector_map = {
        'title': '//div[@class="col-12 text-center title-wrapp"]/h1/text()|//div[contains(@class,"scene-title")]/h1/text()',
        'description': '',
        'date': '//div[@class="col-12 text-center title-wrapp"]/h1/small/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="row position-relative"]//video/@poster',
        'performers': '//h2[contains(text(), "Models")]/following-sibling::dd/a/text()',
        'tags': '//h3[contains(text(), "Tags")]/following-sibling::dd/a/text()',
        'trailer': '//div[@class="row position-relative"]//video/source/@src',
        'external_id': r'video/(.*?)/',
        'pagination': '/en/tour2/scenes/all?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="row justify-content-center"]/div/div[@class="card"]')
        for scene in scenes:
            scenedate = scene.xpath('.//div[contains(@class,"media-info")]/p[@class="text-muted small"]/text()')
            if scenedate:
                meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', self.parse_date(scenedate.get(), date_formats=['%b %d, Y%']).isoformat()).group(1)
            scene = self.format_link(response, scene.xpath('.//a[contains(@href, "/video/")]/@href').get())
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = [s.replace(",", "") for s in performers]
        return performers

    def get_site(self, response):
        site = response.xpath('//h2[contains(text(), "Site")]/following-sibling::dd/a/text()').get()
        return site

    def get_parent(self, response):
        parent = response.xpath('//h2[contains(text(), "Site")]/following-sibling::dd/a/text()').get()
        return parent
