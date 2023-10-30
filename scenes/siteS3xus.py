import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteS3xusSpider(BaseSceneScraper):
    name = 'S3xus'
    site = 'S3xus'
    parent = 'S3xus'
    network = 'S3xus'

    start_urls = [
        'https://s3xus.com/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//ul[@class="info-wrapper"]/li[3]/span/text()',
        'date_formats': ["%b %d, %Y"],
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="model-thumb"]/a/img/@alt',
        'tags': '//div[@class="tag-name"]/a/text()|//p[@class="tags"]/a/text()',
        'duration': '//ul[@class="info-wrapper"]/li[1]/span/text()',
        'external_id': r'scenes/(.+)',
        'trailer': '',
        'pagination': '/scenes?page=%s&order_by=publish_date&sort_by=desc'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="card"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
