import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSuckThisDickSpider(BaseSceneScraper):
    name = 'SuckThisDick'
    network = 'Suck This Dick'
    parent = 'Suck This Dick'
    site = 'Suck This Dick'

    start_urls = [
        'https://suckthisdick.com',
    ]

    selector_map = {
        'title': '//h1[1]/text()',
        'description': '//div[contains(@class, "column mcb-column")]/div/p[not(contains(text(), "Posted by"))]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//div[@class="mcb-wrap-inner"]//video/@poster',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)/',
        'trailer': '//div[@class="mcb-wrap-inner"]//video/source[1]/@src',
        'pagination': '/latest-videos/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h4[@class="entry-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    # ~ #  The date code was used for the initial fill scrape.  It's pretty inaccurate,
    # ~ #  so going forward commenting it out so that current date is used.  Leaving
    # ~ #  the function in as a comment in case it's needed later though.
    # ~ def get_date(self, response):
    # ~ image = response.xpath('//div[@class="mcb-wrap-inner"]//video/@poster')
    # ~ if image:
    # ~ image = image.get()
    # ~ year = re.search(r'uploads/(\d{4})/', image)
    # ~ month = re.search(r'uploads/\d+/(\d{1,2})/', image)
    # ~ if month and year:
    # ~ date = year.group(1) + "-" + month.group(1) + "-01"
    # ~ return self.parse_date(date).isoformat()
    # ~ return self.parse_date('today').isoformat()

    def get_tags(self, response):
        return ['Blowjob']
