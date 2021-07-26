import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteSapphixSpider(BaseSceneScraper):
    name = 'Sapphix'
    network = 'Sapphix'
    parent = 'Sapphix'

    start_urls = [
        'https://www.sapphix.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[@class="mg-md"]/text()',
        'date': '//div[@class="row"]/div[contains(@class,"text-right")]/span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@id="videoPlayer"]//video/@poster',
        'performers': '//h4[contains(text(), "Featured")]/following-sibling::p/a/text()',
        'tags': '//h4[contains(text(), "Tags")]/following-sibling::a/text()',
        'external_id': 'movies\/(.*)\/',
        'trailer': '//div[@id="videoPlayer"]//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="itemm"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Sapphix"
        

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = self.get_from_regex(date.get(), 're_date')

            if date:
                date = date.replace('Added', '').strip()
                date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None

                return dateparser.parse(date, date_formats=date_formats).isoformat()

        return None


    def get_url(self, response):
        url = re.search('(.*)\?nats', response.url)
        if url:
            url = url.group(1)
            return url.strip()
        return response.url
