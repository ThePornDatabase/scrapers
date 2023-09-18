import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkSmutPuppetSpider(BaseSceneScraper):
    name = 'SmutPuppet'
    network = 'Smut Puppet'

    start_urls = [
        'https://smutpuppet.com',
    ]

    selector_map = {
        'title': '//div[@class="section-title"]/h4/text()',
        'description': '//p[@class="read-more"]/text()',
        'date': '',
        'image': '//div[@class="model-player"]/a/img/@src|//video/@poster',
        'performers': '//h4/a[contains(@href, "/models/")]/text()',
        'tags': '//span[contains(text(), "ategories")]/following-sibling::a/text()',
        'external_id': r'update/(\d+)/',
        'trailer': '',
        'pagination': '/updates/?page=%s&latest=1'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-content"]')
        for scene in scenes:
            site = scene.xpath('./div[contains(@class,"item-cblock")]/p/a[contains(@href, "site")]/text()')
            sitename = ''
            if site:
                site = site.get()
                if " - " in site:
                    site = re.search(r'.* - (.*?)$', site)
                    if site:
                        sitename = site.group(1).strip()
                else:
                    sitename = site

            scene = scene.xpath('./div/a/@href').get()
            scene = re.sub(r'(\?.*)', '', scene)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': sitename})

    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site'].strip()
        return "Smut Puppet"

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site'].strip()
        return "Smut Puppet"

    def get_id(self, response):
        sceneid = self.get_from_regex(response.url, 'external_id')
        if not sceneid:
            sceneid = re.search(r'update/(\d+)/', response.url)
            if sceneid:
                sceneid = sceneid.group(1)
        return sceneid
