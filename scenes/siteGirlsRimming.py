import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper

class siteGirlsRimmingSpider(BaseSceneScraper):
    name = 'GirlsRimming'
    network = 'Girls Rimming'
    parent = 'Girls Rimming'

    start_urls = [
        'https://www.girlsrimming.com'
    ]


    selector_map = {
        'title': '',
        'description': '//meta[@name="description"]/@content',
        'performers': '',
        'date': '',
        'image': '//img[contains(@class,"player-thumb-img")]/@src0_4x|//img[contains(@class,"player-thumb-img")]/@src0_3x|//img[contains(@class,"player-thumb-img")]/@src0_2x|//img[contains(@class,"player-thumb-img")]/@src0_1x',
        'tags': '//meta[@name="keywords"]/@content',
        'trailer': '',
        'external_id': '.*\/(.*?).html',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            meta = {}
            meta['site'] = "Girls Rimming"
            meta['parent'] = "Girls Rimming"
            meta['network'] = "Girls Rimming"
            
            title = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a/text()').get()
            if title:
                meta['title'] = title.strip()
                
            performers = scene.xpath('./span[@class="update_models"]/a/text()').getall()
            if performers:
                meta['performers'] = list(map(lambda x: x.strip().title(), performers))
                
            image = scene.xpath('./a/img/@src1_4x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_3x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_2x').get()
            if not image:
                image = scene.xpath('./a/img/@src1_1x').get()
                
            if image:
                meta['image'] = image.strip()
                
            date = scene.xpath('.//div[@class="cell update_date"]/comment()/following-sibling::text()').get()
            if date:
                meta['date'] = dateparser.parse(date.strip()).isoformat()
            
            scene = scene.xpath('./comment()[contains(.,"Title")]/following-sibling::a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
                


    def get_tags(self, response):
        meta = response.meta
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags')).get()
            if tags:
                tags = tags.split(",")
                for performer in meta['performers']:
                    if performer in tags:
                        tags.remove(performer)
                    if "" in tags:
                        tags.remove("")
                tags2 = tags.copy()
                for tag in tags2:
                    matches = [' id ', '...', 'pornstar', 'ramon', 'updates', 'movies', 'anita', 'girlsriming',
                                'models', 'tags', 'photos', 'girlsrimming', '(id:', 'tony', 'totti']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)                    
                tags = list(map(lambda x: x.strip().title(), tags))
                if 'Rimming' not in tags:
                    tags.append('Rimming')
                    
                return tags

        return []
    
    def get_id(self, response):
        if 'external_id' in self.regex and self.regex['external_id']:
            search = self.regex['external_id'].search(response.url)
            if search:
                extern_id = search.group(1)
                return extern_id.lower()

        return None
