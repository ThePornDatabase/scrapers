import re

import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

def match_site(argument):
    match = {
        "blackmeatwhitefeet.com":"Black Meat White Feet",
        "blacksonblondes.com":"Blacks on Blondes",
        "blacksoncougars.com":"Blacks on Cougars",
        "cuckoldsessions.com":"Cuckold Sessions",
        "cumbang.com":"Cumbang",
        "gloryhole-initiations.com":"Gloryhole Initiations",
        "gloryhole.com":"Gloryhole",
        "interracialblowbang.com":"Interracial Blowbang",
        "interracialpickups.com":"Interracial Pickups",
        "watchingmydaughtergoblack.com":"Watching My Daughter Go Black",
        "watchingmymomgoblack.com":"Watching My Mom Go Black",
        "wefuckblackgirls.com":"We Fuck Black Girls",
        "zebragirls.com":"Zebra Girls"
    }
    return match.get(argument, argument)
    

class networkDogfartSpider(BaseSceneScraper):
    name = 'Dogfart'
    network = "Dogfart Network"
    parent = "Dogfart Network"

    start_urls = [
        'https://www.dogfartnetwork.com/',
    ]

    selector_map = {
        'title': '//h1[@class="description-title"]/text()',
        'description': '//meta[@itemprop="description"]/@content',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//div[@class="video-container"]//div[contains(@style,"background")]/@style',
        'performers': '//h4[@class="more-scenes"]/a/text()',
        'tags': '//div[@class="categories"]/p/a/text()',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '', #Trailers are tokenized
        'pagination': '/tour/scenes/?p=%s'
    }


    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"recent-updates")]/a/@href').getall()
        for scene in scenes:
            if "?nats" in scene:
                scene = re.search('(.*)\?nats', scene).group(1)
                if re.search(self.get_selector_map('external_id'), scene):
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_id(self, response):
        search = re.search(self.get_selector_map('external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        search = search.replace("_","-").strip().lower()
        search = re.sub('[^a-zA-Z0-9-]', '', search)
        return search


    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_image(self, response):
        image_text = self.process_xpath(response, self.get_selector_map('image')).get()
        image = re.search('.*url\((.*)\)', image_text).group(1)
        if image:
            image = "https:" + image
            return image
            
        return ''        
        
    def get_site(self, response):
        site = response.xpath('//h3[@class="site-name"]/text()').get()
        if site:
            site = site.strip()
            site = match_site(site.lower())
            return site
        else:
            return "Dogfart Network"
