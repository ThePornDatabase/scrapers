import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class Only3XSpider(BaseSceneScraper):
    name = 'Only3X'
    network = 'Only3X'
    parent = 'Only3X'

    start_urls = [
        'https://only3x.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '',
        'date': '//li/i[@class="icon-eye-open"]/following-sibling::span/following-sibling::text()',
        'image': '//span[@class="update_thumb"]/img/@src',
        'performers': '//li/i[@class="icon-female"]/following-sibling::a/text()',
        'tags': '//span[contains(text(),"Tags")]/following-sibling::a/text()',
        'external_id': 'updates\\/(.*).html',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class,"mpp-playlist-item")]/@data-link').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath(
            '//i[@class="icon-home"]/following-sibling::text()').get()
        if site:
            return site.strip()
        super.get_site(response)

    def get_description(self, response):
        description = response.xpath('//div[@class="set-desc"]').getall()

        if not isinstance(description, str):
            description = " ".join(description)

        description = re.sub('<[^<]+?>', '', description).strip()

        return description
