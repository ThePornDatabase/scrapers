import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieBonVueEnterprisesSpider(BaseSceneScraper):
    name = 'BonVueEnterprises'
    network = 'BonVueEnterprises'
    parent = 'BonVueEnterprises'
    site = 'BonVueEnterprises'

    # Age gate and search prefs only.  VODSESSIONID, AWSALB, AWSALBCORS, logrus and
    # RecMovCat (a browsing-history fingerprint) were removed.
    cookies = {"ageGated": "", "terms": "", "searchType": "movies"}

    start_urls = [
        'https://straight.aebn.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "page-heading-title")]/h1/text()',
        'description': '//div[contains(@class, "page-detail-description-body")]//text()',
        'date': '//li/span[contains(@class, "-detail-list-item-title") and contains(text(), "Released")]/following-sibling::text()',
        'image': '//img[contains(@class,"dts-modal-boxcover-front")]/@src',
        'back': '//img[contains(@class,"dts-modal-boxcover-back")]/@src',
        'performers': '//div[@class="dts-detail-movie-stars-content"]//a[@class="dts-movie-star-wrapper dts-text-link"]/span/text()',
        'tags': '//div[contains(@class,"dts-detail-movie-categories-label")]/following-sibling::div[1]//a/text()',
        'duration': '//li/span[contains(@class, "-detail-list-item-title") and contains(text(), "Running")]/following-sibling::text()',
        'trailer': '',
        'external_id': r'movies/(\d+)/',
        'pagination': '/straight/search/movies/page/<PAGE>?criteria=%7B%22sort%22%3A%22Newest%22%2C%22studioFilters%22%3A%5B14097%5D%7D',
        'type': 'Movie',
    }

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination').replace("<PAGE>", str(page)))

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers = list(dict.fromkeys(performers))
        return performers

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@id, "dtsImageOverlayContainer")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

