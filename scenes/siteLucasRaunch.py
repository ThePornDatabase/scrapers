import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLucasRaunchSpider(BaseSceneScraper):
    name = 'LucasRaunch'
    network = 'Lucas Entertainment'

    start_urls = [
        # ~ 'https://www.lucasraunch.com',
        'https://www.sexinsuits.com',
    ]

    selector_map = {
        'title': '//div[@class="slidercontainer"]//h2/text()',
        'description': '//div[@class="container"]/div[@class="row-fluid"][1]/div[@class="span12"]/p[1]/text()',
        'date': '',
        'image': '//div[contains(@class, "scene-limit-reached")]/img/@src',
        'performers': '//h4/a/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/scenes/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[@class="scene-thumbnail"]/..')
        for scene in scenes:
            scenedate = scene.xpath('.//h6//text()')
            if scenedate:
                scenedate = scenedate.getall()
                scenedate = "".join(scenedate)
                scenedate = re.search(r'(\d{2}\.\d{2}\.\d{2})', scenedate).group(1)
                meta['date'] = self.parse_date(scenedate, date_formats=['%m.%d.%y']).strftime('%Y-%m-%d')
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "content" not in image:
            image = response.xpath('//script[contains(text(), "jwplayer") and contains(text(), "image:")]/text()').get()
            image = image.replace("\r", "").replace("\n", "").replace("\t", "")
            image = re.search(r'jwplayer.*?image:.*?[\'\"](.*?)[\'\"]', image).group(1)
        return self.format_link(response, image)

    def get_site(self, response):
        if "lucasraunch" in response.url:
            return "Lucas Raunch"
        if "sexinsuits" in response.url:
            return "Sex in Suits"

    def get_parent(self, response):
        if "lucasraunch" in response.url:
            return "Lucas Raunch"
        if "sexinsuits" in response.url:
            return "Sex in Suits"
