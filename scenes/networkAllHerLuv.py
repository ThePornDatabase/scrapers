import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AllHerLuvSpider(BaseSceneScraper):
    name = 'AllHerLuv'
    network = 'All Her Luv'

    start_urls = [
        'https://www.allherluv.com',
        'https://www.missax.com'
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//div[@class="container"]/p[contains(@class,"text")]/strong/text()|//p[contains(text(), "Video Description:")]/following-sibling::p//text()',
        'image': '//img[contains(@class,"update_thumb")]/@src0_4x',  # Image is tokened
        'image_blob': True,
        'performers': '//p[@class="dvd-scenes__data"]/a[contains(@href,"/models/")]/text()',
        'tags': '//p[@class="dvd-scenes__data"]/a[contains(@href,"/categories/")]/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',  # tokened, token not in page source
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="photo-thumb_body"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_date(self, response):
        scenedate = response.xpath('//p[contains(@class,"dvd-scenes__data")]//text()[contains(., "Added:")]').get()
        if scenedate:
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate).group(1)
            if scenedate:
                return self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()

    def get_duration(self, response):
        duration = response.xpath('//p[contains(@class,"dvd-scenes__data")]//text()[contains(., "Added:")]')
        if duration:
            duration = duration.get()
            duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None

    def get_site(self, response):
        if "allherluv" in response.url:
            return "All Her Luv"

        if "missax" in response.url:
            return "MissaX"

    def get_image(self, response):
        image = response.xpath(self.get_selector_map('image'))
        if not image:
            image = response.xpath('//img[contains(@class,"update_thumb")]/@src0_3x|//img[contains(@class,"update_thumb")]/@src0_2x|//img[contains(@class,"update_thumb")]/@src0_1x')
        if image:
            image = image.get()
            return self.format_link(response, image)

        return ''
