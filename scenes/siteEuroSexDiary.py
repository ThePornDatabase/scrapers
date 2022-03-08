import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEuroSexDiarySpider(BaseSceneScraper):
    name = 'EuroSexDiary'
    network = 'Euro Sex Diary'
    parent = 'Euro Sex Diary'
    site = 'Euro Sex Diary'

    start_urls = [
        'https://eurosexdiary.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[@class="cntr"]/div[contains(@class, "artl-cnt")]//p|a/text()',
        'date': '//i[@class="fa fa-calendar-o"]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@id="myOverlay"]/amp-img/@src',
        'performers': '//div[@class="update-info"]//a[contains(@href, "/model/")]/text()',
        'tags': '//div[@class="amp-category"]/span/a/text()',
        'external_id': r'.*/(.*?)/$',
        'trailer': '//div[contains(@class, "video-player")]/amp-video/@src',
        'pagination': '/category/conquests/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = super().get_description(response)
        description = re.sub('<[^<]+?>', '', description).strip()
        return description
