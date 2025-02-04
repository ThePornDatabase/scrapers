import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAVEJAVSpider(BaseSceneScraper):
    name = 'AVEJAV'
    network = 'R18'

    start_urls = [
        'https://www.aventertainments.com',
    ]

    selector_map = {
        'title': '//div[@class="section-title"]/h3/text()',
        'description': '',
        'date': '//div[@class="single-info"]/span[contains(text(), "Date")]/following-sibling::span/text()',
        'date_formats': ['%m/%d/%Y'],
        'back': '//span[contains(@class, "grid-gallery")]/a/@href',
        'performers': '//div[@class="single-info"]/span[contains(text(), "Starring")]/following-sibling::span/a/text()',
        'tags': '//div[@class="single-info"]/span[contains(text(), "Category")]/following-sibling::span/a/text()',
        'trailer': '//div[contains(@class, "button-set")]//span/a[contains(@href, "javascript")]/@onclick',
        're_trailer': r'(https.*?)[\'\"]',
        'external_id': r'.com/(\d+)/',
        # ~ 'pagination': '/29/45/1/subdept_products?countpage=%s',
        # ~ 'pagination': '/29/525/1/subdept_products?countpage=%s',
        'pagination': '/29/736/1/subdept_products?countpage=%s',
        'type': 'JAV',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "single-slider-product__image")]/a[1]')
        for scene in scenes:
            image = scene.xpath('./img/@src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        studio = response.xpath('//div[@class="single-info"]/span[contains(text(), "Studio")]/following-sibling::span/a/text()')
        if studio:
            return string.capwords(studio.get().strip())
        return "AV Entertainments"

    def get_parent(self, response):
        return self.get_site(response)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="single-info"]/span[contains(text(), "Play Time")]/following-sibling::span/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_id(self, response):
        sceneid = response.xpath('//div[@class="single-info"]/span[contains(text(), "Item#")]/following-sibling::span/text()')
        if sceneid:
            sceneid = sceneid.get()
            return sceneid.lower().strip()
        return super().get_id(response)

    def get_title(self, response):
        title = string.capwords(super().get_title(response))
        sceneid = self.get_id(response)
        return f"{sceneid.upper()} - {title}"

    def get_performers_data(self, response):
        meta = response.meta
        performers = self.get_performers(response)
        performers_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer
            perf['extra'] = {}
            perf['extra']['gender'] = "Female"
            perf['network'] = "R18"
            perf['site'] = "R18"
            performers_data.append(perf)
        return performers_data

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            matches = ['arrivals', 'blu-ray', 'media', 'release', 'dvd', 'anime', 'sample', 'editor', 'week']
            if not any(x in tag.lower() for x in matches):
                tags2.append(tag)
        return tags2
