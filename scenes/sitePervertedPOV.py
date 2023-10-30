import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePervertedPOVSpider(BaseSceneScraper):
    name = 'PervertedPOV'
    network = 'Perverted POV'
    parent = 'Perverted POV'
    site = 'Perverted POV'

    start_urls = [
        'https://www.pervertedpov.com',
    ]

    selector_map = {
        'title': '//div[@class="video-details"]/div/h1/text()',
        'description': '//div[@class="video-details"]//p/text()',
        'date': '',
        'image': '//video[contains(@id, "player")]/@poster',
        'performers': '//div[@class="video-details"]//span[@class="meta-info"]/following-sibling::a/text()',
        'external_id': r'videos/(.*?)/',
        'pagination': '/videos/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[contains(@class, "type-video")]')
        for scene in scenes:
            duration = scene.xpath('.//strong[contains(text(), "Length")]/following-sibling::text()[1]')
            if duration:
                duration = duration.get()
                if ":" in duration:
                    meta['duration'] = self.duration_to_seconds(duration)
                else:
                    meta['duration'] = str(int(duration) * 60)

            tempimage = scene.xpath('.//img/@data-srcset')
            if tempimage:
                tempimage = tempimage.get()
                tempimage = re.search(r'(.*?\.jpg)', tempimage)
                if tempimage:
                    meta['tempimage'] = tempimage.group(1)

            scene = scene.xpath('./div[1]/a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ["POV"]

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if ".jpg" not in image:
            image = meta['tempimage']
        return image
