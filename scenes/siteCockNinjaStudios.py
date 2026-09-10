import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCockNinjaStudiosSpider(BaseSceneScraper):
    name = 'CockNinjaStudios'
    network = 'Cock Ninja Studios'
    parent = 'Cock Ninja Studios'
    site = 'Cock Ninja Studios'

    start_urls = [
        'https://cockninjastudios.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "entry-title")]/text()',
        'image': '',
        'performers': '//a[contains(@href, "/tag/")]/text()',
        'tags': '//a[contains(@href, "/category/")]/text()',
        'external_id': r'',
        'pagination': '/page/%s/?et_blog',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//article[contains(@class, "pb_post")]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[@class="published"]/text()')
            if scenedate:
                meta['date'] = self.parse_date(scenedate.get()).strftime('%Y-%m-%d')

            sceneid = scene.xpath('./@id')
            if sceneid:
                sceneid = sceneid.get()
                meta['id'] = re.search(r'-(\d+)', sceneid).group(1)

            description = scene.xpath('.//div[contains(@class, "post-content-inner")]/p//text()')
            if description:
                meta['description'] = self.cleanup_description(" ".join(description.getall()).strip())

            sceneurl = scene.xpath('./div[1]/a/@href').get()

            if meta['id'] and self.check_item(meta, self.days):
                image = scene.xpath('.//img/@src')
                if image:
                    meta['image'] = image.get()
                    meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)
