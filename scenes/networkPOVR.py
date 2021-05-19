import dateparser
import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class networkPOVRSpider(BaseSceneScraper):
    name = 'POVR'
    network = 'POVR'
    parent = 'POVR'

    start_urls = [
        'https://povr.com'
    ]

    selector_map = {
        'title': '//h1[@class="player__title"]/text() | //h4/text()',
        'description': '//p[contains(@class,"description")]/text() | //div[@class="player__description"]/p/text()',
        'performers': '//a[contains(@class,"actor")]/text() | //ul/li/a[contains(@class,"btn--eptenary")]/text()',
        'date': '//div[@class="player__meta"]/div[3]/span/text() | //p[@class="player__date"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@class,"tag")]/text() | //ul/li/a[contains(@class,"btn--default")]/text()',
        'site': '//a[contains(@class,"source")]/text() | //ul/li/a[contains(@class,"btn--secondary")]/text()',
        'external_id': '.*-(\d+)$',
        'trailer': '',
        'pagination': '/videos?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="teaser-video"]/a/@href | //a[@class="thumbnail__link"]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = self.process_xpath(response, self.get_selector_map('site')).get()
        if site:
            return site  
        return tldextract.extract(response.url).domain


    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
            if "min" in date or "•" in date and "," in date:
                date = re.search('.*\ (\d{1,2}\ .*\d{4})', date).group(1)
        return dateparser.parse(date.strip()).isoformat()

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).getall()
        if performers:
            return list(map(lambda x: x.strip(), performers))
        else:
            return ["No Performers Listed"]
        return []
