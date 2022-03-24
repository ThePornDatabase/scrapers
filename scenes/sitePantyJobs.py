import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePantyJobsSpider(BaseSceneScraper):
    name = 'PantyJobs'
    network = 'Panty Jobs'
    parent = 'Panty Jobs'
    site = 'Panty Jobs'

    start_urls = [
        'https://www.pantyjobs.com',
    ]

    selector_map = {
        'title': '//section[@class="page-heading"]//h1/text()',
        'description': '//div[@class="post-entry"]/p/text()',
        'date': '//script[@class="yoast-schema-graph"]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//h2[@class="my-3"]/text()',
        'tags': '//div[@class="post-entry"]/span/a/text()',
        'external_id': r'scenes/(.*)/',
        'trailer': '',
        'pagination': '/updates/'
    }

    def start_requests(self):
        link = "https://www.pantyjobs.com/updates/"
        yield scrapy.Request(link, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"vc_gitem-zone-a")]/a[contains(@href, "/scenes/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append('Panties')
        return tags
