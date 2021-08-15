import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteFutileStrugglesSpider(BaseSceneScraper):
    name = 'FutileStruggles'
    network = 'Futile Struggles'


    start_urls = [
        'http://www.futilestruggles.com',
    ]

    selector_map = {
        'title': '//div[@class="title_bar"][1]/text()',
        'description': '//div[@class="gallery_description"]//text()',
        'date': '//div[@class="wrapper"]/table[1]/tr/td[1]/table[1]/tr/td[@class="date"]',
        're_date': '(\d{2}\/\d{2}\/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '',
        'performers': '//td[contains(text(),"Featuring")]/following-sibling::td/a/text()',
        'tags': '//td[contains(text(),"Categories")]/following-sibling::td/a/text()',
        'external_id': 'id=(\d+)',
        'trailer': '',
        'pagination': '/trial/index.php?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//td[@valign="top"]/table')
        for scene in scenes:
            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                meta['image'] =  "http://www.futilestruggles.com" + image.strip()
            else:
                meta['image'] = ''
                
            scene = "http://www.futilestruggles.com/trial/" + scene.xpath('.//a[@class="update_title"]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return "Futile Struggles"

    def get_parent(self, response):
        return "Futile Struggles"
        


    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = title.getall()
            title = "".join(title)
            return title.strip().title()
            
        return ''

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description)
            return description.strip()
            
        return ''

    def get_image(self, response):
        return ''
