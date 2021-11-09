import warnings
from datetime import datetime
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class BadoinkVrSpider(BaseSceneScraper):
    name = 'BadoinkVr'
    network = 'Badoink VR'
    parent = 'Badoink VR'
    max_pages = 100
    start_urls = [
        'https://badoinkvr.com',
        'https://babevr.com',
        'https://18vr.com',
        'http://kinkvr.com',
        'https://vrcosplayx.com',
        'https://realvr.com',
    ]

    selector_map = {
        'title': '//h1[@itemprop="name"]/@content | //h1[contains(@class, "video-title")]/text()',
        'description': '//p[@itemprop="description"]/@content | //p[@class="video-description"]/text()',
        'date': '//p[@itemprop="uploadDate"]/@content | //p[@class="video-upload-date"]/text()',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content | //img[@class="video-image"]/@src',
        'performers': '//a[contains(@class, "video-actor-link")]/text()',
        'tags': "//p[@class='video-tags']//a/text()",
        'external_id': '-(\\d+)\\/?$',
        'trailer': ''
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[@class='tile-grid-item']//a[contains(@class, 'video-card-title')]/@href").getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        selector = '/vrpornvideos?page=%s'

        if 'vrbtrans' in base:
            selector = '/videos?page=%s'
        elif 'vrcosplay' in base:
            selector = '/cosplaypornvideos?page=%s'
        elif 'kinkvr' in base:
            selector = '/bdsm-vr-videos?page=%s'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).get()
        if date:
            return dateparser.parse(date.strip()).isoformat()
        return datetime.now().isoformat()
