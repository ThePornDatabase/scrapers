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
        'https://gangbangaccidents.com',
        'https://gostuckyourself.net',
        'https://youngerloverofmine.com',
        'https://adulttimepilots.com',
        'https://dareweshare.net',
        'https://watchyoucheat.net',


        # To be done in another scraper, not standard format
        # 'https://www.adulttime.com/series/kiss-me-fuck-me', * Done
        # 'https://www.adulttime.com/series/naked-yoga-life', * Done
        # https://www.ladygonzo.com/en/videos * Done
        # https://www.adulttime.com/series/she-wants-him * Done
        # https://www.adulttime.com/series/shower-solos * Done
        # https://www.adulttime.com/series/teen-sneaks * Done
        # https://www.adulttime.com/series/the-mike-and-joanna-show *

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

        if "accident" in response.url:
            return "Accidental Gangbang"

        if "youngerloverofmine" in response.url:
            return "My Younger Lover"

        if "adulttimepilots" in response.url:
            return "Adult Time Pilots"

        if "dareweshare" in response.url:
            return "Dare We Share"

        if "watchyoucheat" in response.url:
            return "Watch You Cheat"

    def get_parent(self, response):
        return "AdultTime"

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get().strip()
        if date:
            if "Days" in date:
                numdays = re.search(r'(\d+)\s+Days', date).group(1)
                if numdays:
                    date = (datetime.today() - timedelta(days=int(numdays))).isoformat()
            else:
                date = dateparser.parse(date).isoformat()
            return date
        else:
            date = response.xpath('//div[@id="title-single"]/span/img[@id="time-single"]/following-sibling::span[1]/text()')
            if date:
                date = date.get()
                if "Yesterday" in date:
                    numdays = 1
                    date = (datetime.today() - timedelta(days=int(numdays))).isoformat()
                    return date

        return None

    def get_tags(self, response):
        tags = []
        if "accident" in response.url:
            tags = ['Gangbang']
        if "joi" in response.url:
            tags = ['JOI', 'Family Roleplay']
        if "mommy" in response.url:
            tags = ['Family Roleplay']
        if "stuck" in response.url:
            tags = ['Stuck Sex']
        if "youngerlover" in response.url:
            tags = ['Older / Younger']
        if "dareweshare" in response.url:
            tags = ['Threesome']
        if "watchyoucheat" in response.url:
            tags = ['Voyeur', 'Adultery', 'Married / Boyfriend / Hotwife']

        return tags
