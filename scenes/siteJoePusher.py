import re
from dateutil.relativedelta import relativedelta
import datetime
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJoePusherSpider(BaseSceneScraper):
    name = 'JoePusher'
    network = 'Joe Pusher'
    parent = 'Joe Pusher'
    site = 'Joe Pusher'

    start_urls = [
        'https://www.joepusher.com',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//span[@class="media-info__desc"]/text()',
        'date': '//span[contains(text(), "Added:")]/following-sibling::strong/text()',
        'image': '//img[contains(@class,"media-container")]/@src',
        'performers': '//div[contains(@class,"media-box")]/following-sibling::div/h3/text()',
        'tags': '//span[contains(text(), "Tags:")]/following-sibling::div/a/text()',
        'duration': '//span[contains(text(), "Duration:")]/following-sibling::strong/text()',
        'trailer': '',
        'external_id': r'videos/(\d+)/',
        'pagination': '/videos/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"item thumb")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_date(self, datestring, date_formats=None):
        today = datetime.datetime.now()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "minute" in datestring:
            date = today - relativedelta(minutes=intervalcount)
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

        return date
