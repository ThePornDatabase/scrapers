import scrapy
import re
import html
import string
import dateparser
import tldextract
from urllib.parse import urlparse

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

def match_site(argument):
    match = {
        'ukpornparty': "UK Porn Party",
        'splatbukkake': "Splat Bukkake",
        'sexyukpornstars': "Sexy UK Pornstars",
        'realasianexposed': "Real Asian Exposed",
    }
    return match.get(argument, argument)
    
class networkUKXXXPassSpider(BaseSceneScraper):
    name = 'UKXXXPass'
    network = 'UK XXX Pass'

    start_urls = [
        'https://ukpornparty.xxx',
        'https://sexyukpornstars.xxx',
        'https://splatbukkake.xxx',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': 'updates\/(.*).html',
        'trailer': '',
        'pagination': '/models/models_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="model"]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
            
    def parse_scene(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()
            
            title = scene.xpath('.//span[contains(@class,"title")]/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''
                

            date = scene.xpath('.//span[contains(@class,"update_date")]/text()').get()
            if date:
                item['date'] = dateparser.parse(date, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = ''
            
            title = scene.xpath('.//span[contains(@class,"title")]/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''                
            
            description = scene.xpath('.//span[contains(@class,"update_description")]/text()').get()
            if description:
                item['description'] = html.unescape(description.strip())
            else:
                item['description'] = ''
            
            
            performers = scene.xpath('.//span[contains(@class,"update_models")]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                item['performers'] = []
                
            
            tags = scene.xpath('.//span[contains(@class,"update_tags")]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip().title(), tags))
            else:
                item['tags'] = []         
                
            
            image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_4x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_3x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_2x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_1x').get()
            if image:
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                item['image'] = base + image.strip().replace(" ","%20")
            else:
                item['image'] = []            
            
            
            trailer = scene.xpath('.//div[@class="update_image"]/a/@onclick').get()
            if trailer:
                trailer = re.search('tload\(\'(.*\.mp4|.*\.m4v)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    item['trailer'] = trailer.strip().replace(" ","%20")
            else:
                item['trailer'] = ''         


            if title:
                externalid = re.sub('[^a-zA-Z0-9-]', '', title)
                item['id'] = externalid.lower().strip().replace(" ","-")
            
            item['url'] = response.url
                
            item['site'] = match_site(tldextract.extract(response.url).domain)
            item['parent'] = match_site(tldextract.extract(response.url).domain)
            item['network'] = "UK XXX Pass"
            
            if item['id'] and item['date']:
                yield item
                
                
        next_page = response.xpath('//comment()[contains(.,"Next Page Link")]/following-sibling::a[1]/@href').get()
        if next_page:
            uri = urlparse(response.url)
            base = uri.scheme + "://" + uri.netloc
            next_page_url = base + "/" + next_page
            yield scrapy.Request(next_page_url, callback=self.parse_scene)
            
