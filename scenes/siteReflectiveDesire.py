import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ReflectiveDesireSpider(BaseSceneScraper):
    name = 'ReflectiveDesire'
    network = 'Reflective Desire'
    parent = 'Reflective Desire'
    site = 'Reflective Desire'

    start_urls = [
        'https://reflectivedesire.com/videos/pain/?sort=chrono',
        'https://reflectivedesire.com/videos/pleasure/?sort=chrono',
        'https://reflectivedesire.com/videos/solos/?sort=chrono',
        'https://reflectivedesire.com/videos/devices/?sort=chrono',
        'https://reflectivedesire.com/videos/extras/?sort=chrono',
    ]

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//meta[@name="description"]/@content',
        're_date': r'Posted ([a-zA-Z]*? \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Performers")]/a/text()',
        'tags': '//span[contains(text(), "Categories")]/a/text()',
        'external_id': r'.*\/(.*?)\/',
        'trailer': '',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//main/section[1]//article/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = ['Bondage', 'Fetish', 'Latex / Rubber / Vinyl']
        tags2 = super().get_tags(response)
        for tag in tags2:
            tags.append(tag)
        return tags

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = self.get_from_regex(date.get(), 're_date')
            if date:
                date = date.replace(" ", " 1, ")
                return self.parse_date(date).isoformat()
        return self.parse_date('today').isoformat()

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = performers.getall()
            return list(map(lambda x: x.replace("Follow ", "").strip(), performers))
        return []
