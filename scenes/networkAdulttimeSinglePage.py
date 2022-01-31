import re
from datetime import datetime, timedelta
import scrapy
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class AdultTimeSinglePageSpider(BaseSceneScraper):
    name = 'AdultTimeSinglePage'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://mommysboy.net',
        'https://cardiogasm.net',
        'https://caughtfapping.net',
        'https://joimom.net',
        'https://gostuckyourself.net',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@id="header-inside"]/p/text()',
        'date': '//div[@id="title-single"]/span/img[@id="time-single"]/following-sibling::text()',
        'image': '//video/@poster',
        'image_blob': True,
        'performers': '//div[@id="title-single"]/strong[contains(text(),"Starring")]/following-sibling::a/text()',
        'tags': '',
        'external_id': r'.*\/(.*?)\/$',
        'trailer': '//video/source/@src',
        'pagination': '/categories/movies_%s_d.html#'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link,
                                 callback=self.get_scenes,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@id="title-posta"]/h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        if "cardiogasm" in response.url:
            return "Cardiogasm"

        if "joi" in response.url:
            return "JOI Mom"

        if "fapping" in response.url:
            return "Caught Fapping"

        if "mommy" in response.url:
            return "Mommys Boy"

        if "stuck" in response.url:
            return "Go Stuck Yourself"

    def get_parent(self, response):
        return "AdultTime"

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            if "Days" in date:
                numdays = re.search(r'(\d+)\s+Days', date).group(1)
                if numdays:
                    date = (datetime.today() - timedelta(days=int(numdays))).isoformat()
            else:
                date = dateparser.parse(date).isoformat()

            return date

        return None
