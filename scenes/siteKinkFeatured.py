import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class KinkFeaturedSpider(BaseSceneScraper):
    name = 'KinkFeatured'
    network = "Kink"

    start_urls = [
        'https://www.kink.com'
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//span[@class="description-text"]/p/text()',
        'date': "//span[@class='shoot-date']/text()",
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//p[@class="starring"]/span/a/text()',
        'tags': "//a[@class='tag']/text()",
        'external_id': '\\/shoot\\/(\d+)',
        'trailer': '//meta[@name="twitter:player"]/@content',
        'pagination': '/shoots/featured?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//a[@class='shoot-link']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return response.xpath('//div[@class="shoot-page"]/@data-sitename').get().strip()
        
    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        performers_stripped = [s.strip() for s in performers]      
        performers_stripped = [s.rstrip(',') for s in performers_stripped]      
        return list(map(lambda x: x.strip(), performers_stripped))    
