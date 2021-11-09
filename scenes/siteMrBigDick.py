import re
import scrapy
import dateparser
import json

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class siteMrBigfatdickSpider(BaseSceneScraper):
    name = 'MrBigfatdick'
    network = 'MrBigfatdick'

    start_urls = [
        "https://backend.mrbigfatdick.com",
    ]

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/public/videos?p=%s&s=50'
    }

    def get_scenes(self, response):
        global json
        movies = json.loads(response.text)
        
        for movie in movies:
            item = SceneItem()
            
            item['title'] = movie['fullName'].strip().title()
            item['description'] = ''

            item['performers'] = []
            for performer in movie['models']:
                item['performers'].append(performer['fullName'].strip().title())

            item['image'] = movie['previewImage960']

            item['date'] = dateparser.parse(movie['publishDate']).isoformat()
            
            item['tags'] = []
            for tag in movie['tags']:
                item['tags'].append(tag['fullName'].strip().title())            
            
            # ~ item['trailer'] = movie['videoSrc_1920']
            item['trailer'] = ''
            
            item['site'] = "MrBigfatdick"
            item['parent'] = "MrBigfatdick"
            item['network'] = "MrBigfatdick"
            item['url'] = "https://www.mrbigfatdick.com/videos/" + movie['permaLink']
            item['id'] = movie['id']

            yield item

    def get_next_page_url(self, base, page):
        page = str(int(page)-1)
        return self.format_url(base, self.get_selector_map('pagination') % page)
