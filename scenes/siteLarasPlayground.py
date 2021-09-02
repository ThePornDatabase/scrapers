import scrapy
import string
import html
import dateparser
import re

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

class sitLarasPlaygroundSpider(BaseSceneScraper):
    name = 'LarasPlayground'
    network = 'Laras Playground'
    max_pages = 35

    start_urls = [
        'https://www.larasplayground.com'
    ]

    selector_map = {
        'title': r'//h1[contains(@class, "title")]/text()',
        'description': r'//p[contains(@class, "description")]/text()',
        'performers': r'//span[contains(@class,"models")]/a/text()',
        'date': r'//div[contains(@class, "date")]/text()',
        'image': r'//meta[@property="og:image"]/@content',
        'tags': r'//div[contains(@class, "video-tags")]/a/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/index.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="serie"]')
        if response.meta['page'] < self.max_pages:
            for scene in scenes:
                item = SceneItem()
                title = scene.xpath('./div/div[@class="serie_tekst"]/strong/text()').get()
                if title:
                    item['title'] = html.unescape(string.capwords(title))
                else:
                    item['title'] = ''

                description = scene.xpath('./div/div[@class="serie_tekst"]/strong/following-sibling::text()').get()
                if description:
                    item['description'] = html.unescape(description)
                else:
                    item['description'] = ''

                item['performers'] = ['Lara Latex']
                item['tags'] = []
                item['date'] = dateparser.parse('today').isoformat()

                image = scene.xpath('./div/div[@class="serie_pic01"]/img/@src').get()
                if image:
                    item['image'] = image.strip()
                else:
                    item['image'] = []

                item['trailer'] = ''
                item['site'] = "Laras Playground"
                item['parent'] = "Laras Playground"
                item['network'] = "Laras Playground"

                extern_id = re.search('.*\/(\d+)\/.*?\.jpg', item['image'])
                if extern_id:
                    item['id'] = extern_id.group(1).strip()

                item['url'] = response.url

                yield item
