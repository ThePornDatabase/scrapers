import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class CumPerfectionSpider(BaseSceneScraper):
    name = 'HookupHotshot'
    network = "Hookup Hotshot"
    parent = "Hookup Hotshot"

    start_urls = [
        'https://hookuphotshot.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class,"videoDetails")]/h3/text()',
        'description': '',
        'date': '//span[contains(text(),"Date Added")]/following-sibling::text()',
        'image': '//script[contains(text(),"video_content")]/text()',
        'performers': '//li[@class="update_models"]/a/text()',
        'tags': '//li[@class="label"]/following-sibling::li/a[contains(@href,"categories")]/text()',
        'external_id': '.*\\/(.*?)\\.html',
        'trailer': '//script[contains(text(),"video_content")]/text()',
        'pagination': '/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="item-thumb"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        trailer = self.process_xpath(
            response, self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search('src=\"(.*.mp4)\"', trailer)
            if trailer:
                trailer = trailer.group(1)
                trailer = trailer.replace(" ", "%20")
                trailer = "https://hookuphotshot.com" + trailer
                return trailer
        return ''


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('poster=\"(.*.jpg)\"', image)
            if image:
                image = image.group(1)
        else:
            image = response.xpath('//img[contains(@class,"update_thumb")]/@src0_1x').get()
            
        if image:
            image = image.replace(" ", "%20")
            image = "https://hookuphotshot.com" + image
            return image
        else:
            return ''
        

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []        

    def get_description(self,response):
        return ''

    def get_site(self, response):
        return "Hookup Hotshot"
