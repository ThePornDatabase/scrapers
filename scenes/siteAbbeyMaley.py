import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper

### Abbiemaley.com has all scenes hidden behind a paywall.
### Sexyhub seems to have recent updates, and is getting current ones as 
### well, so I'm pulling from there.

class siteAbbieMaleySpider(BaseSceneScraper):
    name = 'AbbieMaley'
    network = "Abbie Maley"
    parent = "Abbie Maley"

    start_urls = [
        'https://www.sexyhub.org',
    ]

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[contains(text(),"Description")]/following-sibling::div[1]/text()',
        'date': '//div[contains(text(),"Release Date")]/following-sibling::text()',
        'date_formats': ['%d %b %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="models"]/a/text()',
        'tags': '//div[contains(text(),"Categories")]/following-sibling::span/a/text()',
        'external_id': '.*\/\d+-(.*)-abbiemaley',
        'trailer': '',
        'pagination': '/xfsearch/site/AbbieMaley.com/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h2[@class="title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        if performers:
            performerlist = []
            for performer in performers:
                performer = performer.lower()
                if " aka " in performer:
                    performer = re.search('(.*) aka ', performer).group(1)
                if performer:
                    performerlist.append(performer.strip().title())
            return list(map(lambda x: x.strip().title(), performerlist))

        return []


    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).getall()
            if tags:
                performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
                if performers:
                    for performer in performers:
                        if performer in tags:
                            tags.remove(performer)
                for tag in tags:
                    if " aka " in tag.lower():
                        tags.remove(tag)
            return list(map(lambda x: x.strip(), tags))

        return []
        
        
    def get_site(self, response):
        return "Abbie Maley"
