import re
from datetime import datetime
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Part of the Tugpass network, but not included on their index, and different enough that it's easier to just make a new scraper


class FamilyLustSpider(BaseSceneScraper):
    name = 'FamilyLust'
    network = "TugPass"
    max_pages = 25

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
        'external_id': '\\/videos\\/(.*).htm',
        'trailer': '',
        'pagination': '/updates_%s.html'
    }

    # This is one of those sites with Date and Site on the index, so have to
    # pull it from the outer loop
    def get_scenes(self, response):
        parentxpath = response.xpath('//div[contains(@class,"updateDetails")]')

        for child in parentxpath:
            date = child.xpath("./h4/text()").get()
            date = date.replace("Date: ", "")
            if date[-1] == ",":
                date = date[:-1].strip()
            date = dateparser.parse(date).isoformat()
            site = "Family Lust"

            scene = child.xpath("./h3/a/@href").get()
            if "?nats" in scene:
                scene = re.search("(.*)(\\?nats)", scene).group(1).strip()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta={'date': date, 'site': site})

    def get_date(self, response):
        return datetime.now().isoformat()

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if image:
            image = "https://www.familylust.com/" + image
            return self.format_link(response, image)
        return ''

    def get_parent(self, response):
        return "Family Lust"
