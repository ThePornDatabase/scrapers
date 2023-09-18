import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHeyHoneyClubSpider(BaseSceneScraper):
    name = 'HeyHoneyClub'
    network = 'Hey Honey Club'
    parent = 'Hey Honey Club'
    site = 'Hey Honey Club'

    start_urls = [
        'https://heyhoneyclub.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/all-videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item preview"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//a/b/text()').get())
            item['date'] = scene.xpath('.//div[@class="date"]/text()').get()
            item['performers'] = scene.xpath('.//div[@class="model"]/a/text()').getall()
            item['image'] = self.format_link(response, scene.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['description'] = ''
            item['tags'] = []
            item['trailer'] = None
            item['site'] = "Hey Honey Club"
            item['parent'] = "Hey Honey Club"
            item['network'] = "Hey Honey Club"
            item['url'] = self.format_link(response, scene.xpath('./a[1]/@href').get())
            item['id'] = re.search(r'.*/(.*)$', item['url']).group(1)
            if "release-" in item['id']:
                item['id'] = re.search(r'release-(\d+)', item['id']).group(1)
            yield self.check_item(item, self.days)
