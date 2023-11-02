import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTransationalFantasiesSpider(BaseSceneScraper):
    name = 'TransationalFantasies'
    network = 'Transational Fantasies'

    start_urls = [
        'https://www.transationalfantasies.com',
    ]

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    selector_map = {
        'title': '//div[@class="modal-header"]/h5/text()',
        'description': '//div[@class="synopsis"]/p/text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()[1]',
        'date_formats': ['%B %d, %Y'],
        'image': '//style[contains(text(), "poster-image-background")]/text()',
        're_image': r'poster-image-background:before.*?(http.*?)\)',
        'performers': '//div[@class="video-performer"]/a/img/@title',
        'tags': '//span[contains(text(), "Categories:")]/following-sibling::a/text()',
        'duration': '//span[contains(text(), "Length:")]/following-sibling::text()',
        're_duration': r'(\d+)',
        'director': '//div[@class="director"]/a/text()',
        'trailer': '',
        'external_id': r'.*/(\d+)/.*',
        'pagination': '/watch-transational-fantasies-free-trailers.html?page=%s&hybridview=member',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "item_")]/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = super().get_duration(response)
        if duration:
            duration = str(int(duration) * 60)
        return duration

    def get_site(self, response):
        site = response.xpath('//div[@class="studio"]/a/text()')
        if site:
            site = self.cleanup_title(site.get())
        if not site:
            site = "Transational Fantasies"
        return site

    def get_parent(self, response):
        return "Transational Fantasies"

    def get_image(self, response):
        image = response.xpath('//style[contains(text(), "poster-image-background")]/text()')
        if image:
            image = image.get()
            image = image.replace("\r", "").replace("\n", "").replace("\t", "").replace("  ", " ")
            image = re.search(r'poster-image-background:before.*?(http.*?)\)', image)
            if image:
                image = image.group(1)
        return image
