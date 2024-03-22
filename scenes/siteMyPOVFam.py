import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMyPOVFamSpider(BaseSceneScraper):
    name = 'MyPOVFam'
    network = 'My POV Fam'
    parent = 'My POV Fam'
    site = 'My POV Fam'

    start_urls = [
        'https://www.mypovfam.com',
    ]

    selector_map = {
        'title': '//div[@class="video-details"]/div[1]/h1/text()',
        'description': '//div[@class="video-details"]//p/text()',
        'image': '//video/@poster',
        'performers': '//div[@class="video-details"]//span[@class="meta"]//a/text()',
        'external_id': r'',
        'trailer': '//video//source/@src',
        'pagination': '/videos/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[contains(@class, "type-video")]')
        for scene in scenes:
            sceneid = scene.xpath('.//@class').get()
            if "post-" in sceneid:
                meta['id'] = re.search(r'post-(\d+)', sceneid).group(1)

            duration = scene.xpath('.//strong[contains(text(), "Length:")]/following-sibling::text()[1]')
            if duration:
                duration = duration.get()
                meta['duration'] = self.duration_to_seconds(duration)

            images = scene.xpath('.//img/@srcset')
            if images:
                images = images.get()
                images = images.split(",")
                image = images[-1]
                meta['image'] = re.search(r'(.*) ', image).group(1).strip()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./div[1]/a[1]/@href').get()

            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
