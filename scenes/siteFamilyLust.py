import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Part of the Tugpass network, but not included on their index, and different enough that it's easier to just make a new scraper


class FamilyLustSpider(BaseSceneScraper):
    name = 'FamilyLust'
    network = "TugPass"
    parent = "TugPass"
    site = "TugPass"

    max_pages = 30

    start_urls = [
        'https://www.familylust.com'
    ]

    selector_map = {
        'title': '//div[@class="videoblock"]/h2/text()',
        'description': '//div[@class="epDescription"]/strong/following-sibling::text()',
        'date': "//div[@class='views']/span/text()",
        'image': '//div[@class="video_here"]/img/@src',
        'performers': '//div[@class="featuringWrapper"]/a/text()',
        'tags': "",
        'external_id': r'/videos/(.*).htm',
        'trailer': '',
        'pagination': '/updates_%s.html'
    }

    def get_scenes(self, response):
        parentxpath = response.xpath('//div[contains(@class,"updateDetails")]')

        for child in parentxpath:
            date = child.xpath("./h4/text()").get().replace("Date: ", "")
            if date[-1] == ",":
                date = date[:-1].strip()
            date = self.parse_date(date).isoformat()

            scene = child.xpath("./h3/a/@href").get()
            if "?nats" in scene:
                scene = re.search("(.*)(\\?nats)", scene).group(1).strip()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})
