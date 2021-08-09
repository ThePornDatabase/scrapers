import scrapy
import re
import html
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteSweetyXSpider(BaseSceneScraper):
    name = 'SweetyX'
    network = 'SweetyX'

    url = 'https://www.sweetyx.com/en/sweetyx-videos'

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="video_description"]/div/div/p/text()',
        'date': '//div[@class="video_description"]//span[@class="info"]/span/span[contains(text(),"Date")]/../following-sibling::span/text()',
        'date_formats': ['%d/%m/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video_description"]//span[@class="info"]/span[contains(@class,"data-model")]/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': '.*\/(.*?)$',
        'trailer': '',
        'pagination': ''
    }


    def start_requests(self):
        yield scrapy.Request(url=self.url,
                             callback=self.get_scenes,
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//article/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "SweetyX"

    def get_parent(self, response):
        return "SweetyX"
        

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description)
            return html.unescape(description.strip())

        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                
                tags = tags.get()
                if "," in tags:
                    tags = tags.split(",")
                    tags = list(map(lambda x: x.strip().lower(), tags))

                    performers = self.process_xpath(response, self.get_selector_map('performers')).get()
                    if performers:
                        if "," in performers:
                            performers = performers.split(",")
                        elif "&" in performers:
                            performers = performers.split("&")
                        else:
                            performers = [performers]                        
                        performers = list(map(lambda x: x.strip().lower(), performers))
                        
                        for performer in performers:
                            if performer in tags:
                                tags.remove(performer)        
                
                tags2 = tags.copy()
                for tag in tags2:
                    matches = ['uncle bob', 'brozerland', 'sweetyx']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)
                
                if '' in tags:
                    tags.remove('')
                
                    
            if tags:
                return list(map(lambda x: x.strip().title(), tags))

        return []



    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).get()
        if performers:
            if "," in performers:
                performers = performers.split(",")
            elif "&" in performers:
                performers = performers.split("&")
            else:
                performers = [performers]                    
            return list(map(lambda x: x.strip().title(), performers))

        return []
