import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteLoadMyMouthSpider(BaseSceneScraper):
    name = 'LoadMyMouth'
    network = 'Load My Mouth'


    start_urls = [
        'http://www.loadmymouth.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '//strong[contains(text(),"Release Date")]/following-sibling::text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::span/text()',
        'tags': '',
        'external_id': 'num=([a-zA-Z]{1,2}\d+)',
        'trailer': '',
        'pagination': '/home.php?page=%s'
    }

    def get_scenes(self, response):
        meta = {}
        scenes = response.xpath('//div[@class="item_wrapper" and not(.//text()[contains(.,"PHOTOSETS")])]')
        for scene in scenes:
            image = scene.xpath('.//div[@class="img_wrapper"]/a[1]/img/@src').get()
            if image:
                meta['image'] = image.strip()
            else:
                meta['image'] = ''
                
            tags = scene.xpath('.//div[@class="tags"]/span/text()')
            if tags:
                tags = list(map(lambda x: x.strip().title(), tags.getall()))
                tags = "".join(tags).strip()
                tags = tags.split(",")
                tags = list(map(lambda x: x.strip().title(), tags))
                if '' in tags:
                    tags.remove('')
                meta['tags'] = tags
            else:
                meta['tags'] = []    
            
            scene = scene.xpath('.//div[@class="play_btn"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return "Load My Mouth"

    def get_parent(self, response):
        return "Load My Mouth"
        

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).get()
        if performers:
            if "," in performers:
                performers = performers.split(",")
            else:
                performers = [performers]
            return list(map(lambda x: x.strip().title(), performers))

        return []

