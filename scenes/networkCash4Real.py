import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkCash4RealSpider(BaseSceneScraper):
    name = 'Cash4Real'
    network = 'Cash4Real'
    parent = 'Cash4Real'

    start_urls = [
        # ~ 'https://www.cumclinic.com',
        # ~ 'https://www.gloryholeswallow.com',
        'https://www.spytug.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'image': '//div[@class="player-thumb"]//img/@src0_1x',
        'image_blob': True,
        'tags': '//i[@class="fa fa-tags"]/following-sibling::span/a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'playsinline src=\"(.*?\.mp4)',
        'external_id': r'trailers/(.*).html',
        'pagination': '/tour/categories/Movies_%s_d.html'
    }

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination')
        if "spytug" in base:
            pagination = pagination.replace("/tour/", "/")
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/trailers/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        if "cumclinic" in response.url:
            return "Cum Clinic"
        if "gloryholeswallow" in response.url:
            return "Glory Hole Swallow"
        if "spytug" in response.url:
            return "Spy Tug"
        return super().get_site(response)

    def get_parent(self, response):
        if "cumclinic" in response.url:
            return "Cum Clinic"
        if "gloryholeswallow" in response.url:
            return "Gloryhole Swallow"
        if "spytug" in response.url:
            return "Spy Tug"
        return super().get_parent(response)
