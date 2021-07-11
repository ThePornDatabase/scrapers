import re
import dateparser
import scrapy
import html
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class ArchangelVideoSpider(BaseSceneScraper):
    name = 'ArchangelVideo'
    network = "Archangel"
    parent = "Archangel"

    start_urls = [
        'https://www.archangelvideo.com/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '.*\/(.*?)\.html',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-episode"]')
        scenelist = []
        for scene in scenes:
            item = SceneItem()
            item['site'] = "Archangel"
            item['parent'] = "Archangel"
            item['network'] = "Archangel"
            title = scene.xpath('.//h3/a/text()').get()
            if title:
                item['title'] = string.capwords(title.strip())
                item['title'] = html.unescape(item['title'])
            else:
                item['title'] = 'No Title Available'

            date = scene.xpath('.//strong[contains(text(),"Date")]/following-sibling::text()').get()
            if date:
                date = dateparser.parse(date.strip()).isoformat()
                item['date'] = date
            else:
                item['date'] = "1970-01-01T00:00:00"            

            performers = scene.xpath('./div[@class="item-info"]//a[contains(@href,"/models/")]/text()').getall()
            if len(performers):
                item['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                item['performers'] = []
                
            image = scene.xpath('.//span[@class="left"]/a/img/@src0_1x').get()
            if image:
                image = image.replace('//','/').strip()
                image = image.replace('#id#','').strip()
                image = "https://www.archangelvideo.com" + image
                item['image'] = image.strip()
            else:
                item['image'] = ''

            item['trailer'] = ''
            
            url = scene.xpath('.//span[@class="left"]/a/@href').get()
            if url:
                item['url'] = url.strip()
                external_id = re.search('.*\/(.*).html', url).group(1)
                if external_id:
                    item['id'] = external_id.strip().lower()
                else:
                    item['id'] = ''
            else:
                item['url'] = ''
                
            item['description'] = ''
            item['tags'] = []
                
            if item['title'] and item['id']:
                scenelist.append(item.copy())
            
            item.clear()
        
        return scenelist
                
                
            
