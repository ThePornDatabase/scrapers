import re
import warnings
import html
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class SitePornDudeCastingSpider(BaseSceneScraper):
    name = 'PornDudeCasting'
    network = 'Porn Dude Casting'

    start_urls = [
        'https://porndudecasting.com',
    ]

    selector_map = {
        'title': '//h1[@class="header__nav-user-name"]/text()',
        'description': '//span[@class="desc icon"]/div/text()',
        'date': '//li[@class="model__info-item"]/span[contains(text(), "Cast")]/following-sibling::span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="model__img"]//h5[@class="model__head-name"]/text()',
        'tags': '//div[@class="btn btn--green btn--small header__login-btn"]/text()',
        'external_id': r'casting/(\d+)/',
        'trailer': '',
        'pagination': '/latest-updates/'
    }

    def start_requests(self):
        url = "https://porndudecasting.com/latest-updates/"
        yield scrapy.Request(url,
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb__gallery"]/div/a[@class="thumb__gallery-col"][1]/@data-href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Porn Dude Casting"

    def get_parent(self, response):
        return "Porn Dude Casting"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description)
            return html.unescape(description.strip())

        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Professional Model" in tags:
            tags.remove("Professional Model")
        return tags

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = date.get()
            date = date.strip().replace(" ", " 1, ")
            return dateparser.parse(date).isoformat()
        return None
