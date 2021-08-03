import scrapy
import re
import html
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHegreSpider(BaseSceneScraper):
    name = 'Hegre'
    network = 'Hegre'


    start_urls = [
        'https://www.hegre.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//div[contains(@class,"record-description")]/div/p//text()',
        'date': '//div[contains(@class,"date-and-covers")]/span/text()',
        'image': '//div[contains(@class,"video-player-wrapper")]/@style',
        're_image': '(http.*\.jpg)',
        'performers': '//div[contains(@class,"record-models")]/a/@title',
        'tags': '//div[contains(@class,"current-tags")]/div/a/text()',
        'external_id': '.*\/(.*?)$',
        'trailer': '//video/source[contains(@type,"mp4")]/@src',
        're_trailer': '(.*)\?',
        'pagination': '/movies?films_sort=most_recent&films_page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Hegre"

    def get_parent(self, response):
        return "Hegre"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''        


    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            return dateparser.parse(date).isoformat()
        else:
            return dateparser.parse('today').isoformat()

        return None
