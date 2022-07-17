import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteStraightGuysForGayEyesSpider(BaseSceneScraper):
    name = 'StraightGuysForGayEyes'
    network = 'Straight Guys For Gay Eyes'
    parent = 'Straight Guys For Gay Eyes'
    site = 'Straight Guys For Gay Eyes'

    start_urls = [
        'https://www.straightguysforgayeyes.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"video_details")]/div/h3/text()',
        'description': '//div[contains(@class,"video_details")]//div[contains(@class,"aboutvideo")]//text()',
        'date': '',
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*?\.jpg)',
        'performers': '//ul[@class="featuredModels"]//a[contains(@href, "models/")]/span/text()',
        'tags': '',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=\"(.*?\.mp4)',
        'external_id': r'.*/(.*?)\.html',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "/trailers/")]/../..')
        for scene in scenes:
            image = scene.xpath('.//a[contains(@href, "/trailers/")]/img/@src0_1x').get()
            meta['id'] = re.search(r'.*/(\d+)-', image).group(1)

            scenedate = scene.xpath('.//p[contains(@class, "timing")]//text()').getall()
            scenedate = " ".join(scenedate).strip()
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
            else:
                scenedate = '01/01/2022'
            meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()

            scene = scene.xpath('.//a[contains(@href, "/trailers/")]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
