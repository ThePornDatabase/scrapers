import re
from datetime import datetime, timedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFightingDollsSpider(BaseSceneScraper):
    name = 'FightingDolls'
    network = 'Fighting Dolls'

    start_urls = [
        'https://www.trib-dolls.com',
        'https://www.fighting-dolls.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h3[contains(text(),"Description")]/following-sibling::p//text()',
        'date': '//div[@class="categories"]/text()',
        'image': '//div[@id="sample"]/img/@src',
        'performers': '//div[@class="grid-x"]/div/div/div/h3/a/text()',
        'tags': '//div[@class="categories"]/a/text()',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': ''
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="card-image"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        if "trib-dolls" in response.url:
            return "Trib Dolls"
        return "Fighting Dolls"

    def get_parent(self, response):
        if "trib-dolls" in response.url:
            return "Trib Dolls"
        return "Fighting Dolls"

    def get_next_page_url(self, base, page):
        if "fighting-dolls" in base:
            pagination = '/all-fighting-dolls-videos/%s/'
        if "trib-dolls" in base:
            pagination = '/all-trib-dolls-videos/%s/'
        page = str(int(page) - 1)
        return self.format_url(base, pagination % page)

    def get_date(self, response):
        date = response.xpath('//div[@class="categories"]/text()').getall()
        if date:
            date = "".join(date)
            date = re.search(r'(\d+) day', date)
            if date:
                daysago = int(date.group(1))
                date = datetime.now() - timedelta(days=daysago)
                if date:
                    return date.isoformat()
        return self.parse_date('today').isoformat()
