import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNaughtyAlyshaSpider(BaseSceneScraper):
    name = 'NaughtyAlysha'
    network = 'Pornicate'
    parent = 'Naughty Alysha'
    site = 'Naughty Alysha'

    start_urls = [
        'https://www.naughtyalysha.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "videoDetails")]/h3/text()',
        'description': '//div[contains(@class, "videoDetails")]/p//text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?\.jpg)',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[contains(text(), "Tags:")]/following-sibling::li/a[contains(@href, "categories")]/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=\"(.*?\.mp4)',
        'external_id': r'.*/(.*?)\.html',
        'pagination': '/tour/categories/Movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            duration = scene.xpath('.//div[@class="time"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d{1,2}:\d{1,2})', duration)
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))
            image = scene.xpath('./div/a/img/@src0_1x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scenedate = scene.xpath('.//div[@class="time"]/following-sibling::comment()')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get())
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1)).isoformat()
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or ".jpg" not in image:
            image = response.xpath('//div[@class="player-thumb"]//img[contains(@class, "update_thumb")]/@src0_2x')
            if image:
                return self.format_link(response, image.get())
        return image
