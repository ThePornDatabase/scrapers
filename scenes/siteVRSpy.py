import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRSpySpider(BaseSceneScraper):
    name = 'VRSpy'
    site = 'VRSpy'
    parent = 'VRSpy'
    network = 'VRSpy'

    start_urls = [
        'https://vrspy.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "section-header-container")]/text()',
        'description': '//div[contains(@class,"show-more-text-container")]//text()',
        'date': '//div[contains(text(), "Release date")]/span[1]/text()|//div[contains(text(), "Release date")]/following-sibling::div[1]/text()',
        'date_formats': ['%d %B %Y'],
        'image': '//meta[@property="og:image"]/@content[contains(., "cover")]',
        'performers': '//div[contains(@class,"video-actor-item")]/span/text()',
        'tags': '//div[@class="video-categories"]/a//text()',
        'duration': '//div[contains(text(), "Duration:")]/span[1]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?sort=new&page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.vrspy.com/videos?sort=new"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"item-wrapper")]//div[@class="photo"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.xpath('//script[contains(@id, "NUXT_DATA")]/text()')
            if image:
                image = image.get()
                image = re.search(r'\"Video\".*?(https.*?cover.jpg)', image)
                image = image.group(1)
        if image and image not in response.url:
                return image
        return ""

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Virtual Reality" not in tags:
            tags.append("Virtual Reality")
        return tags

    def get_title(self, response):
        title = super().get_title(response)
        if " - Vr" in title:
            title = re.search(r'(.*?) - Vr', title).group(1)
        return title
