import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePureXXXSpider(BaseSceneScraper):
    name = 'PureXXX'
    network = 'Pure-XXX'
    parent = 'Pure-XXX'
    site = 'Pure-XXX'

    start_urls = [
        'https://www.pure-xxx.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "video_membership")]/div[contains(@class, "titlebox")]/h3/text()',
        'description': '//div[contains(@class,"aboutvideo")]/p/text()',
        'date': '//div[contains(@class,"video_description")]/h4[1]/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//section//div[contains(@class,"videohere")]/img/@src',
        'performers': '//ul[@class="featuredModels"]/li/a/span[not(contains(@class, "Thumb"))]/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'trailers/(.*?)\.htm',
        'pagination': '/tour/updates/page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "empire clear")]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('date'))
        if duration:
            duration = duration.get().strip()
            duration = duration.replace("&nbsp;", " ")
            sceneduration = 0
            if "minute" in duration.lower():
                minutes = re.search(r'(\d{1,3})\s+?min', duration)
                if minutes:
                    minutes = minutes.group(1)
                    sceneduration = int(minutes) * 60
                if "second" in duration.lower():
                    seconds = re.search(r'(\d{1,2})\s+?sec', duration)
                    if seconds:
                        seconds = seconds.group(1)
                        sceneduration = sceneduration + int(seconds)
                if sceneduration:
                    return str(sceneduration)
        return None

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "content" not in image:
            image = response.xpath('//script[contains(text(), "jwplayer") and contains(text(), "image")]/text()')
            if image:
                image = image.get()
                image = re.search(r'image: ?\"(/tour.*?contentthumb.*?\.jpg)', image)
                if image:
                    image = image.group(1)
                    return self.format_link(response, image)
        return image

    def get_trailer(self, response):
        trailer = response.xpath('//script[contains(text(), "jwplayer") and contains(text(), "image")]/text()')
        if trailer:
            trailer = trailer.get()
            trailer = re.search(r'file: ?\"(/tour.*?\.mp4)', trailer)
            if trailer:
                return self.format_link(response, trailer.group(1))
        return None
