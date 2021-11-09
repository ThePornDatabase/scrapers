import warnings
import dateparser
import scrapy
from scrapy.http import HtmlResponse

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class FiveKPornSpider(BaseSceneScraper):
    name = '5kporn'
    network = '5kporn'
    parent = '5kporn'

    start_urls = [
        'https://www.5kporn.com'
    ]

    cookies = {'nats': 'MC4wLjEuMS4wLjAuMC4wLjA'}

    selector_map = {
        'title': "//p[@class='trailer-title']/text()",
        'description': '//div[contains(@class, "video-summary")]//p[@class=""]/text()',
        'date': "//div[@class='row video-summary']/div/h5[4]/text()",
        'image': '//div[contains(@class, "gal")]//img/@src',
        'performers': '//h5[contains(., "Starring")]/a/text()',
        'tags': "",
        'external_id': 'episodes\\/(.+)',
        'trailer': '',
        'pagination': '/episodes/search?page=%s'
    }

    def get_scenes(self, response):
        rsp = HtmlResponse(url=response.url, body=response.json()[
                           'html'], encoding='utf-8')
        for scene in rsp.css('.thumb-holder a::attr(href)').getall():
            yield scrapy.Request(url=scene, callback=self.parse_scene, cookies=self.cookies)

    def get_date(self, response):
        date = response.xpath('//h5[contains(text(), "Published")]/text()')
        if date:
            date = date.get()
            return dateparser.parse(date.replace('Published:', '').strip()).isoformat()
        return dateparser.parse('today').isoformat()
