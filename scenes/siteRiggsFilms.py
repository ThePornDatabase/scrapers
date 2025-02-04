import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class SiteRiggsFilmsSpider(BaseSceneScraper):
    name = 'RiggsFilms'
    network = 'Riggs Films'
    parent = 'Riggs Films'
    site = 'Riggs Films'

    start_urls = [
        'https://riggsfilms.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h1/following-sibling::p[not(contains(.//a/@data-wpel-link, "internal"))]/text()',
        'date': '//meta[@property="ya:ovs:upload_date"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"][1]/@content',
        'performers': '//strong[contains(text(), "Starring")]/a/text()',
        'tags': '',
        'duration': '//strong[contains(text(), "Duration")]/following-sibling::text()[1]',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'type': 'Scene',
        'pagination': '/scenes/page/%s/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h5/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
