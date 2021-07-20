import scrapy
import string
import html
import dateparser 
import re

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class networkPanoramaPacificSpider(BaseSceneScraper):
    name = 'PanoramaPacific'
    network = 'Panorama Pacific'
    parent = 'This is Glamour'

    start_urls = [
        'https://www.thisisglamour.com/'
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
        'pagination': 'https://www.thisisglamour.com/glamour-videos/?start=%s&count=25'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="product-item"]')
        for scene in scenes:
            item = SceneItem()
            
            title = scene.xpath('./h3/a/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title))
            else:
                item['title'] = ''
            
            item['description'] = ''
            
            performers = scene.xpath('./div[@class="pi-model"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []
            
            item['tags'] = []
            
            date = scene.xpath('./div[@class="pi-added"]/text()').get()
            if date:
                item['date'] = dateparser.parse(date.strip(), date_formats=['%d %b %Y']).isoformat()
            else:
                item['date'] = []
            
            image = scene.xpath('./div[contains(@class,"pi-img")]/a/img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = []
                
            if item['image']:
                extern_id = re.search('galid\/(\d+)\/',item['image']).group(1)
                if extern_id:
                    item['id'] = extern_id.strip()
            
            item['trailer'] = ''
            item['site'] = "This Is Glamour"
            item['parent'] = "This Is Glamour"
            item['network'] = "Panorama Pacific"

            item['url'] = "https://www.thisisglamour.com/"

            yield item



    def get_next_page_url(self, base, page):
        offset = (int(page) * 25) + 1
        return self.format_url(base, self.get_selector_map('pagination') % str(offset))
