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
        'title': '//div[@class="updateInfo"]/h2/text()',
        'description': '//div[@class="updateDescription"]/p/text()',
        'date': '',
        'image': '//div[contains(@class,"blockUpdates")]/div[contains(@class, "exclusive_update")]/a/img/@src',
        'performers': '//div[@class="updateModels"]/a/text()',
        'tags': '',
        'external_id': r'count/(\d+)/',
        'trailer': '',
        'pagination': '/tour/?cat=latest&page_num=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoThumb"]')
        for scene in scenes:
            site = scene.xpath('./div[contains(@class,"videoDetails")]/p/text()')
            sitename = ''
            if site:
                site = site.get()
                if " - " in site:
                    site = re.search(r'.* - (.*?)$', site)
                    if site:
                        sitename = site.group(1).strip()

            scene = scene.xpath('./a/@href').get()
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
