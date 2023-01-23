import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTukTukPatrolSpider(BaseSceneScraper):
    name = 'TukTukPatrol'
    network = 'Tuk Tuk Patrol'
    parent = 'Tuk Tuk Patrol'
    site = 'Tuk Tuk Patrol'

    start_urls = [
        'https://tuktukpatrol.com',
    ]

    selector_map = {
        'title': '//div[@class="cntr"]/h1/text()',
        'description': '//div[contains(@style,"padding-top")]/h2//following-sibling::text()',
        'date': '',
        'image': '//div[contains(@class, "video-player")]//amp-img/@src',
        'performers': '//i[@class="fa fa-female"]/following-sibling::a/text()',
        'tags': '//div[@class="amp-category"]/span/a/text()',
        'duration': '//div[@class="update-info"]/i[contains(@class, "video-camera")]/following-sibling::text()',
        're_duration': r'(\d{1,2}:\d{2}(?::\d{2})?)',
        'trailer': '//div[contains(@class, "video-player")]//amp-video/@src',
        'external_id': r'content/(.*)/',
        'pagination': '/all-updates/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article')
        for scene in scenes:
            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
