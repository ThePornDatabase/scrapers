import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMassageGirls18Spider(BaseSceneScraper):
    name = 'MassageGirls18'
    network = 'MassageGirls18'
    parent = 'MassageGirls18'
    site = 'MassageGirls18'

    start_urls = [
        'http://massagegirls18.com',
    ]

    selector_map = {
        'title': '//title/text()',
        're_title': r'(.*) - ',
        'description': '',
        'date': '//td[@class="date"]/comment()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "jwplayer")]/text()',
        're_image': r'image: ?\"(/member.*?contentthumb.*?\.jpg)',
        'performers': '//a[contains(@class, "model_category_link") and contains(@href, "sets.php")]/text()',
        'tags': '//a[contains(@class, "model_category_link") and contains(@href, "category.php")]/text()',
        'duration': '',
        'trailer': '//script[contains(text(), "jwplayer")]/text()',
        're_trailer': r'file.*?(http.*?)[\"\']',
        'external_id': r'id=(\d+)',
        'pagination': '/membersarea/index.php?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "thumb")]/a/@href').getall()
        for scene in scenes:
            if "&nats" in scene:
                scene = re.search(r'(.*)\&nats', scene).group(1)
            scene = "membersarea/" + scene
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "content" not in image:
            image = response.xpath('//script[contains(text(), "img_video.src")]/text()')
            if image:
                image = image.get()
                image = re.search(r'(/member.*?contentthumb.*?\.jpg)', image)
                if image:
                    image = image.group(1)
                    return self.format_link(response, image)
        return image
