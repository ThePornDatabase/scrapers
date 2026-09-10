import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTiedGirlsSpider(BaseSceneScraper):
    name = 'TiedGirls'
    network = 'TiedGirls'
    parent = 'TiedGirls'
    site = 'TiedGirls'

    start_urls = [
        'https://tiedgirls.com',
    ]

    selector_map = {
        'title': '//h4/text()[contains(., "TG")]',
        'description': '//div[contains(@class,"vidImgContent") and contains(@class, "text_light")]//text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="gallery_vod_buttons"]/following-sibling::p[contains(@class, "link_light")]/a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="gallery_vod_buttons"]/following-sibling::div[@class="blogTags"]/ul/li/a/text()',
        'external_id': r'(TG\w+)',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@id, "packageinfo")]')
        for scene in scenes:

            scenedate = scene.xpath("./text()").get()
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%Y-%m-%d']).strftime('%Y-%m-%d')

            meta['url'] = self.format_link(response, scene.xpath("./following-sibling::h4/a/@href").get())
            if meta['url']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)
