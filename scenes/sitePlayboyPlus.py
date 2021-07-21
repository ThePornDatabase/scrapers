import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper

class sitePlayboyPlusSpider(BaseSceneScraper):
    name = 'PlayboyPlus'
    network = "Playboy"
    parent = "Playboy"
    
    headers =  {
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    start_urls = [
        'https://www.playboyplus.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"headline-container")]/h1/text()',
        'description': '//p[contains(@class,"description")]//text()',
        'date': '//p[@class="date label"]/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="imageContainer"]//picture/source[1]/@data-srcset',
        'performers': '//p[@class="contributorName"]/a/text()',
        'tags': '//div[contains(@class,"headline-container")]/a[contains(@class,"tag")]/text()',
        'external_id': '.*\/(.*)$',
        'trailer': '',
        'pagination': '/updates?page=%s&order=most-recent'
    }

    def get_scenes(self, response):
        
        htmlcode = response.text
        results = re.findall('cardLink.*?href=\\\\"(.*?)\\\\"', htmlcode)
        for scene in results:
            scene = "https://www.playboyplus.com" + scene.replace("\\","")
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
        
    def get_site(self, response):
        return "Playboy Plus"


    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)   
            description = description.replace(" ... ","").replace("\n","").replace("  ","")
            return description.strip()

        return ''


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            # ~ imagelist = re.findall('(https:\/\/.*?)\s\d{2,5}w',image)
            imagelist = re.findall('(https:\/\/.*?.jpg)',image)
            if len(imagelist):
                image = imagelist[0]
            
        if image:
            image = image.replace(" ","%20")
            return self.format_link(response, image)
        else:
            return ''
