import re
import warnings
import string
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class SiteRubberPassionSpider(BaseSceneScraper):
    name = 'RubberPassion'
    network = 'Rubber Passion'

    start_urls = [
        'https://tour.rubber-passion.com',
    ]

    selector_map = {
        'title': '//h3[@class="video-title"]/text()',
        'description': '//div[contains(@class, "video-info")]/p[1]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//figure/img/@src',
        'performers': '',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/category/updates/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[@class="post"]')
        for scene in scenes:
            date = dateparser.parse('today').isoformat()
            datestring = scene.xpath('.//p[@class="video-added"]/text()')
            if datestring:
                datestring = datestring.get()
                datestring = re.search(r'(\w+ \d{1,2}, \d{4})', datestring)
                if datestring:
                    date = dateparser.parse(datestring.group(1)).isoformat()
            title = scene.xpath('./div/a/@title').get()
            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and "gallery" not in title.lower():
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_site(self, response):
        return "Rubber Passion"

    def get_parent(self, response):
        return "Rubber Passion"

    def get_performers(self, response):
        return ['Latex Lucy']

    def get_title(self, response):
        title = super().get_title(response)
        title = string.capwords(title.replace("‘", "").replace("’", "").strip())
        return title
