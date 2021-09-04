import scrapy
import re
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class siteSinsLifeSpider(BaseSceneScraper):
    name = 'SinsLife'
    network = 'Sins Life'

    start_urls = [
        'https://sinslife.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '.*\/(.*?)\/$',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        SceneList = []
        scenes = response.xpath('//div[@class="item "]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['image'] = ''
            item['description'] = ''
            item['network'] = "Sins Life"
            item['parent'] = "Sins Life"
            item['site'] = "Sins Life"

            title = scene.xpath('.//div[contains(@class,"item-title")]/a/text()').get()
            if title:
                item['title'] = title.strip()
                externalid = re.sub('[^a-zA-Z0-9-]', '', item['title'])
                item['id'] = externalid.lower().strip().replace(" ","-")
                
            item['url'] = response.url

            description = scene.xpath('.//div[@class="item-meta"]/div/text()').getall()
            if description:
                description = " ".join(description)
                description = description.replace("  ", " ")
                item['description'] = description.strip()

            item['date'] = dateparser.parse('today').isoformat()

            image = scene.xpath('.//img/@src0_3x').get()
            if not image:
                image = scene.xpath('.//img/@src').get()

            if image:
                item['image'] = image.strip()

            if item['id'] and item['title'] and item['date']:
                SceneList.append(item.copy())
                item.clear()

        return SceneList

