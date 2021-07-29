import scrapy
import re
import string
import html
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHeavyOnHottiesSpider(BaseSceneScraper):
    name = 'HeavyOnHotties'
    network = 'Heavy On Hotties'
    parent = 'Heavy On Hotties'

    start_urls = [
        'https://www.heavyonhotties.com',
    ]

    selector_map = {
        'title': '//h2/span/following-sibling::text()',
        'description': '//div[contains(@class,"comment-section")]/div/p/text()',
        'date': '//span[@class="released title"]/strong/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//video/@poster',
        'performers': '//span[@class="feature title"]/strong/a[contains(@href,"/models/")]/text()',
        'tags': '',
        'external_id': '.*\/(.*?)$',
        'trailer': '//video/source/@src',
        'pagination': '/movies/page-%s/?tag=&q=&model=&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"star")]/a[contains(@href, "/movies/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Heavy On Hotties"
        

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = self.get_from_regex(title.get(), 're_title')

            if title:
                title = title.replace('In:','').replace('"','')
                return string.capwords(html.unescape(title.strip().title()))

        return None        


    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(response, self.get_selector_map('trailer'))
            if trailer:
                trailer = self.get_from_regex(trailer.get(), 're_trailer')
                trailer = self.format_link(response, trailer)
                return trailer.replace(" ", "%20")

        return ''


    def get_tags(self, response):
        return []
