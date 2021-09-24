import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWhoaBoyzSpider(BaseSceneScraper):
    name = 'WhoaBoyz'
    network = 'Whoa Boyz'

    start_urls = [
        'https://www.whoaboyz.com',
    ]

    selector_map = {
        'title': '//div[@class="trailer"]/h2/text()',
        'description': '//div[@class="trailer"]/p[1]/text()',
        'date': '//p[@class="date-trailer"]/span/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="trailer"]//span[@class="tour_update_models"]/a/text()',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '//div[@class="trailervid"]/div/video/source/@src',
        'pagination': '/tour/categories/Movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-title"]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Whoa Boyz"

    def get_parent(self, response):
        return "Whoa Boyz"
