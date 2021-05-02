import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from datetime import datetime
import dateparser

class NymphoSpider(BaseSceneScraper):
    name = 'Nympho'
    network = "Nympho"

    start_urls = [
        'https://tour.allanal.com',
        'https://tour.analonly.com',
        # ~ 'https://tour.nympho.com', #Currently blocked by StackPath, can't fully test
        'https://tour.swallowed.com',
        'https://tour.trueanal.com'
    ]

    selector_map = {
        'title': '',
        'description': '//div[contains(@class,"desc")]/p/text()',
        'date': "",
        'image': '//div[@class="overlay-limit"]/@style',
        'performers': '//div[@class="content-page-info"]//h4[@class="models"]/a/text()',
        'tags': "", #Tags not available
        'external_id': '\/view\/(.*?)\/',
        'trailer': '//video/source/@src',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        if 'swallowed' in response.request.url:
            nymphoxpath = "//h3[@class='title']/a/@href"

        if 'trueanal' in response.request.url:
            nymphoxpath = "//div[@class='content-meta']/h3[@class='title']/a/@href"

        matches = ["allanal", "analonly", "nympho"]
        if any(x in response.request.url for x in matches):   
            nymphoxpath = "//div[contains(@class,'content-card-info')]/h4[@class='content-title-wrap']/a/@href"
            
        scenes = response.xpath(nymphoxpath).getall()

        for scene in scenes:
            scene = scene + "/"
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        matches = ["trueanal", "swallowed"]
        if any(x in response.request.url for x in matches):            
            nymphoxpath = "//span[@class='post-date']/span[@class='fa fa-calendar']/following-sibling::text()"

        matches = ["allanal", "analonly", "nympho"]
        if any(x in response.request.url for x in matches):            
            nymphoxpath = "//div[@class='content-page-info']//span[contains(@class,'mobile-date')]/text()"
                    
        date = response.xpath(nymphoxpath).get()
        # ~ date.replace('Released:', '').replace('Added:', '').strip()
        return dateparser.parse(date.strip()).isoformat()

                        
    def get_site(self, response):
        if 'allanal' in response.request.url:
            return "All Anal"
        if 'analonly' in response.request.url:
            return "Anal Only"
        if 'nympho' in response.request.url:
            return "Nympho"
        if 'swallowed' in response.request.url:
            return "Swallowed"
        if 'trueanal' in response.request.url:
            return "True Anal"

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url + "/", re.IGNORECASE)
        return search.group(1)

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        image = re.search("url\((.*)\)", image).group(1)
        return self.format_link(response, image)

    def get_title(self, response):
        if 'trueanal' in response.request.url:
            nymphoxpath = "//h1[@class='title']/text()"
            
        matches = ["allanal", "analonly", "nympho", "swallowed"]
        if any(x in response.request.url for x in matches):   
            nymphoxpath = "//h2[@class='title']/text()"
        
        return response.xpath(nymphoxpath).get().strip()
