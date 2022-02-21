import re
import datetime
from dateutil.relativedelta import relativedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


# A few things about this scraper:
# 1) There is no page 1 with regular pagination.  Pagination picks up on Page 2, so custom starting url
# 2) There are no dates on scenes, instead just "xx days/weeks/months/years" ago, so it's calculated
#    This is going to cause a lot of mismatched dates on initial import, but should be good for recent stuff
#    At the time of writing the newest scene is 2 days ago, so I'm guessing on "today" and "yesterday"


class SiteCumLouderSpider(BaseSceneScraper):
    name = 'CumLouder'
    network = "Cum Louder"
    parent = "Cum Louder"

    start_urls = [
        'https://www.cumlouder.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//strong[contains(text(),"Description")]/following-sibling::text()',
        'date': '//strong[contains(text(),"Added")]/following-sibling::text()',
        'image': '//link[@rel="preload" and @as="image" and contains(@href,".jpg")]/@href',
        'image_blob': '//link[@rel="preload" and @as="image" and contains(@href,".jpg")]/@href',
        'performers': '//a[@class="pornstar-link"]/text()',
        'tags': '//a[@class="tag-link"]/text()',
        'external_id': r'.*porn-video/(.*)\/$',
        'trailer': '',
        'pagination': '/%s/?s=last'
    }

    def start_requests(self):
        yield scrapy.Request(url="https://www.cumlouder.com/porn/?s=last",
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href,"/porn-video/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Cum Louder"

    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.replace("_", "-").strip()
        return search

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return title.strip().title()
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_date(self, response):
        today = datetime.datetime.now()
        datestring = self.process_xpath(response, self.get_selector_map('date')).get()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "hour" in datestring:
            date = today - relativedelta(hours=intervalcount)
        if "day" in datestring:
            date = today - relativedelta(days=intervalcount)
        if "today" in datestring:
            date = today
        if "yesterday" in datestring:
            date = today - relativedelta(days=1)
        if "week" in datestring:
            date = today - relativedelta(weeks=intervalcount)
        if "month" in datestring:
            date = today - relativedelta(months=intervalcount)
        if "year" in datestring:
            date = today - relativedelta(years=intervalcount)

        return date.isoformat()
