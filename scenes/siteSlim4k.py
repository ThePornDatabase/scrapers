import re
import datetime
from dateutil.relativedelta import relativedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSlim4kSpider(BaseSceneScraper):
    name = 'Slim4k'
    network = 'Slim4k'

    start_urls = [
        'https://www.slim4k.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//span[contains(text(), "Submitted:")]/em/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="item" and contains(text(), "Models:")]/a/text()',
        'tags': '//div[@class="item" and contains(text(), "Tags:")]/a/text()',
        'external_id': r'videos/(\d+)/',
        'trailer': '',
        'pagination': '/latest-updates/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="list-videos"]/div/div/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Slim4k"

    def get_parent(self, response):
        return "Slim4k"

    def get_date(self, response):
        today = datetime.datetime.now()
        datestring = self.process_xpath(response, self.get_selector_map('date')).get()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
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
