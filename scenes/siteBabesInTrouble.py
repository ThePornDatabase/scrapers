import re
from datetime import datetime

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# They don't have a site any longer, so pulling information from an index site

class siteBabesInTroubleSpider(BaseSceneScraper):
    name = 'BabesInTrouble'
    network = "Babes In Trouble"
    parent = "Babes In Trouble"

    start_urls = [
        'https://www.clips4sale.com'
    ]

    selector_map = {
        'title': '//h3[@class="[ text-white mt-3-0 mb-1-0 text-2-4 ]"]/text()',
        'description': '//div[@class="individualClipDescription"]/p/text()',
        'date': '//span[contains(text(),"Added")]/span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//span[@class="relatedCatLinks"]/span/a/text()',
        'external_id': '.*\/(.*)$',
        'trailer': '',
        'pagination': '/studio/37354/babes-in-trouble/Cat0-AllCategories/Page%s/ClipDate-desc/Limit96/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//span[@class="thumb_format" and contains(text(),"WMV")]/../following-sibling::div/div/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site':"Babes In Trouble"})

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        extern_id = search.group(1)
        if extern_id:
            extern_id = extern_id.lower().replace("-wmv","")
        return extern_id.strip()

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            title = title.lower()
            title = title.replace("enhanced hd quality", "")
            title = title.replace("wmv", "")
            title = title.replace(" - ", "")
            title = title.title()
            return title.strip()
        return ''


    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []
        
    def get_performers(self,response):
        return []
