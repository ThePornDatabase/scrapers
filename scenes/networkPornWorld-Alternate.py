# Fixed old sites to scrape historical

import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from datetime import datetime
import dateparser

class PornWorldScraper(BaseSceneScraper):
    name = 'PornWorldAlt'
    network = 'ddfnetwork'

    start_urls = [
        'https://www.sandysfantasies.com/',
        'https://cherryjul.com/',
        'https://eveangelofficial.com/',
        'https://sexvideocasting.com/',
        'https://hairytwatter.net/'
    ]

    selector_map = {
        'title': "//h1[@class='videotitle']/text()",
        'description': "//p[@class='vText']/text()",
        'date': "",
        'image': '//video/@poster',
        'performers': "",
        'tags': "",
        'external_id': 'videos\/.*\/(\d+)',
        'trailer': '',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@class='videoPic']/a/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        search = re.search('Added:\ (.*?\d{2,4})\ {1,3}', response.text)
        return dateparser.parse(search.group(1)).isoformat()

    def get_performers(self, response):
        performers = []

    def get_image(self, response):
        if 'sandysfantasies' in response.request.url:
            selector = '//div[@class="videoPlayerContainer"]/img/@src'
        matches = ["cherryjul", "eveangelofficial", "sexvideocasting", "hairytwatter"]
        if any(x in response.request.url for x in matches):
            selector = '//video/@poster'    
                        
        image = self.process_xpath(response, selector).get()
        return self.format_link(response, image)
