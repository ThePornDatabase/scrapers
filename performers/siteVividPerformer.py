import scrapy
import html
from urllib.parse import urlparse


from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem

class networkOlderWomanFunPornstarSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/stars/api/?flagCeleb=N&limit=24&offset=%s&sort=datedesc',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'VividPerformer'
    network = "Vivid"

    start_urls = [
        'https://www.vivid.com',
    ]

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['responseData']
        for performer in jsondata:
            item = PerformerItem()

            item['name'] = performer['stagename']
            item['image'] = performer['placard']
            item['gender'] = performer['gender']
            item['url'] = self.format_link(response, performer['url'])
            item['network'] = 'Vivid'
            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url
