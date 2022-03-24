import re
import datetime
import dateparser
from dateutil.relativedelta import relativedelta
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'cashforsextape': 'Cash For Sextape',
        'chickiporn': 'ChickiPorn',
        'hardfucktales': 'Hard Fuck Tales',
        'mypickupgirls': 'My Pickup Girls',
        'porntraveling': 'Porn Traveling',
        'studentsexparties': 'Student Sex Parties',
    }
    return match.get(argument, argument)


class NetworkSeriousPartnersSpider(BaseSceneScraper):
    name = 'WTFPassAlt'
    network = 'WTFPass'

    start_urls = [
        'https://cashforsextape.com',
        'https://chickiporn.com',
        'https://hardfucktales.com',
        'https://mypickupgirls.com',
        'https://porntraveling.com',
        'https://studentsexparties.com',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@name="description"]/@content',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "data-actress")]/a[@class="link-red model-link-overlay"]/text()',
        'tags': '//div[@class="video-page-tab-info"]//a[contains(@href, "categories")]/text()',
        'external_id': r'videos/(\d+)/',
        'trailer': '',
        'pagination': '/videos/%s/'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[@class="thumb-video cf"]')
        for scene in scenes:

            meta['date'] = self.parse_date('today').isoformat()
            date = scene.xpath('.//span[@class="date-added"]/text()')
            if date:
                date = date.get()
                date = parse_date(date)
                if date:
                    meta['date'] = date
            else:
                meta['date'] = dateparser.parse('today').isoformat()

            scene = scene.xpath('./div/a[contains(@href,"/videos/")]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)


def parse_date(datestring):
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

    return date.isoformat()
