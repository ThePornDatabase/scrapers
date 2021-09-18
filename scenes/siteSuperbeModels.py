import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSuperbeModelsSpider(BaseSceneScraper):
    name = 'SuperbeModels'
    network = 'Superbe Models'

    start_urls = [
        'https://www.superbemodels.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class,"description-video")]/p/text()',
        'date': '//span[@class="duration-title" and contains(text(), "date")]/following-sibling::em/text()',
        'image': '//script[contains(text(), "preview_url")]/text()',
        're_image': r'preview_url: \'(http.*.jpg)',
        'performers': '//a[contains(@class,"models-name-box")]/text()',
        'tags': '//span[@class="title-tag-video"]/following-sibling::a/text()',
        'external_id': r'videos/(\d+)/',
        'trailer': '',
        'pagination': '/films/featured/?mode=async&function=get_block&block_id=list_videos_common_videos_list&sort_by=post_date&from=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "item")]/a[contains(@href, "/videos/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Superbe Models"

    def get_parent(self, response):
        return "Superbe Models"

    def get_tags(self, response):
        tags = super().get_tags(response)
        return list(map(lambda x: x.replace(",", "").strip().title(), tags))
