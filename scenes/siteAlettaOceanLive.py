import re
import dateparser
import scrapy
import html
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class AlettaOceanLiveSpider(BaseSceneScraper):
    name = 'AlettaOceanLive'
    network = "Aletta Ocean Live"
    parent = "Aletta Ocean Live"

    start_urls = [
        'https://alettaoceanlive.com/',
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
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movie-set-list-item"]')
        scenelist = []
        for scene in scenes:
            item = SceneItem()
            item['site'] = "Aletta Ocean Live"
            item['parent'] = "Aletta Ocean Live"
            item['network'] = "Aletta Ocean"
            title = scene.xpath('.//div[contains(@class,"title")]/text()').get()
            if title:
                item['title'] = string.capwords(title.strip())
                item['title'] = html.unescape(item['title'])
            else:
                item['title'] = 'No Title Available'

            date = scene.xpath('.//div[contains(@class,"date")]/text()').get()
            if date:
                date = dateparser.parse(date.strip()).isoformat()
                item['date'] = date
            else:
                item['date'] = "1970-01-01T00:00:00"            

            item['performers'] = ['Aletta Ocean']
                
            image = scene.xpath('./@style').get()
            if image:
                image = re.search('url\((.*.jpg)', image).group(1)
                if image:
                    item['image'] = image.strip()
            else:
                item['image'] = ''

            item['trailer'] = ''
            
            url = scene.xpath('./a/@href').get()
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
                
                
            
