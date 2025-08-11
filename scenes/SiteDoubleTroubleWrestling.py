import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDoubleTroubleWrestlingSpider(BaseSceneScraper):
    name = 'DoubleTroubleWrestling'
    network = 'DoubleTroubleWrestling'
    parent = 'DoubleTroubleWrestling'
    site = 'DoubleTroubleWrestling'

    start_urls = [
        'https://shop.dtwrestling.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(text(), "Description")]/following-sibling::p[1]//text()',
        'image': '//div[@class="woocommerce-product-gallery__wrapper"]/div[1]/a[contains(@href, "jpg")]/@href',
        'performers': '//span[contains(@class, "posted_in")]/a[contains(@href, "wrestler")]/text()',
        'external_id': r'.*/(.*?)/',
        'pagination': '/index.php/product-category/dl/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//ul[contains(@class, "products")]/li/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "short-description")]//p[contains(text(), "min")]/text()')
        if not duration:
            duration = response.xpath('//p//text()[contains(., "Time:")]')
        if duration:
            duration = duration.get().lower().strip()
            duration = re.sub(r'[^0-9a-z]+', '', duration)
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_tags(self, response):
        return ['Sports', 'Wrestling']

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = ""
        return image
