import scrapy
import string
import html
import dateparser 
import re

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class siteLegsJapanSpider(BaseSceneScraper):
    name = 'LegsJapan'
    network = 'Digital J Media'
    parent = 'Legs Japan'

    start_urls = [
        'https://www.legsjapan.com'
    ]


    selector_map = {
        'title': '',
        'description': '',
        'performers': '',
        'date': '',
        'image': '',
        'tags': '',
        'trailer': '',
        'external_id': '',
        'pagination': '/en/samples?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('(//div[@class="tContent left"]|//div[@class="tContent right"])')
        for scene in scenes:
            item = SceneItem()
            
            title = scene.xpath('.//h3[1]/strong/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title))
            else:
                item['title'] = ''
            
            description = scene.xpath('.//h3[1]/strong/text()').get()
            if description:
                item['description'] = html.unescape(description)
            else:
                item['description'] = ''
            
            performers = scene.xpath('.//h1/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []
            
            tags = scene.xpath('.//h4[contains(text(),"tags")]/strong/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip(), tags))
            else:
                item['tags'] = []
            
            date = scene.xpath('.//h3[contains(text(),"released")]/strong/text()').get()
            if date:
                item['date'] = dateparser.parse(date, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = []
            
            image = scene.xpath('./preceding-sibling::div[1]/@style').get()
            if image:
                image = re.search('(https:.*.jpg)', image).group(1)
                if image:
                    item['image'] = image.strip()
            else:
                item['image'] = []
                
            if item['image']:
                extern_id = re.search('samples\/(.*?)\/',item['image']).group(1)
                if extern_id:
                    item['id'] = extern_id.strip()
                    item['trailer'] = "https://cdn.legsjapan.com/samples/" + extern_id.strip() + "/sample.mp4"
            
            
            item['site'] = "Legs Japan"
            item['parent'] = "Legs Japan"
            item['network'] = "Digital J Media"

            item['url'] = "https://www.legsjapan.com/en/samples/" + item['id']

            yield item
