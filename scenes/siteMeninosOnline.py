import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMeninosOnlineSpider(BaseSceneScraper):
    name = 'MeninosOnline'
    site = 'Meninos Online'
    parent = 'Meninos Online'
    network = 'Meninos Online'

    start_urls = [
        'https://www.meninosonline.net',
    ]

    selector_map = {
        'title': '//h3[@class="text-center"]/text()',
        'image': '//div[@class="pnl-player"]/img/@src',
        'external_id': r'.*/(.*)?$',
        'pagination': '/en/movies?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="pnl-mini"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="duration"]/text()').get()
            if scenedate:
                scenedate = self.parse_date(scenedate, date_formats=['%m-%d-%Y'])
                meta['date'] = scenedate.strftime('%Y-%m-%d') if scenedate else None

            scene = scene.xpath('./a[1]/@href').get()
            if scene and re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if "(" in title:
            title = re.search(r'(.*)?\(', title).group(1)
        title = self.cleanup_title(title)
        return title.strip()

    def get_performers(self, response):
        performers = []
        title = self.get_title(response)
        if "-" in title:
            title = re.search(r'(.*?)-', title).group(1)
            if "&" in title:
                performers = title.split("&")
                performers = list(map(lambda x: string.capwords(x.strip()), performers))
        return performers

    def get_tags(self, response):
        return ['Gay']
