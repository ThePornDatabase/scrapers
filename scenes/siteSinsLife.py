import re

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSinsLifeSpider(BaseSceneScraper):
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
        'external_id': r'.*\/(.*?)\/$',
        'trailer': '',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        scenelist = []
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
                item['title'] = self.cleanup_title(title)
                externalid = re.sub('[^a-zA-Z0-9-]', '', item['title'])
                item['id'] = externalid.lower().strip().replace(" ", "-")

            item['url'] = response.url

            description = scene.xpath('.//div[@class="item-meta"]/div/text()').getall()
            if description:
                description = " ".join(description)
                description = description.replace("  ", " ")
                item['description'] = self.cleanup_description(description)

            item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//img/@src0_3x').get()
            if not image:
                image = scene.xpath('.//img/@src').get()

            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            if item['id'] and item['title'] and item['date']:
                scenelist.append(item.copy())
                item.clear()

        return scenelist
