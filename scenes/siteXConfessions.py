import scrapy
import re
import html

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteXConfessionsSpider(BaseSceneScraper):
    name = 'XConfessions'
    network = 'XConfessions'
    parent = 'XConfessions'

    start_urls = [
        'https://xconfessions.com/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2/..//text()',
        'date': '//script[contains(text(),"NUXT")]/text()',
        're_date': 'production_date=\"(.*?)\";',
        'image': '//div[contains(@class,"w-1/3")][1]/div/div/picture/source/@data-srcset',
        're_image': '(.*)\?',
        'performers': '//div[contains(@class,"w-1/3")]//a[@data-cy="performer-link"]/text()',
        'tags': '//div[contains(@class,"w-1/3")]//a[contains(@href,"/categories/")]/text()',
        'external_id': '.*\/(.*)',
        'trailer': '',
        'pagination': '/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@data-cy,"hover-wrapper")]/a[contains(@href,"/film")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "XConfessions"
        

    def get_description(self, response):
        desc_rows = self.process_xpath(response, self.get_selector_map('description')).getall()
        if desc_rows:
            description = ''
            for desc in desc_rows:
                desc = desc.strip()
                if desc:
                    description = description + " " + desc
            return html.unescape(description.strip())

        return ''
