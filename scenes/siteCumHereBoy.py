import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCumHereBoySpider(BaseSceneScraper):
    name = 'CumHereBoy'

    start_urls = [
        'https://cumhereboy.com',
    ]

    selector_map = {
        'title': './/h4/a/text()',
        'image': './/video/@poster_4x',
        'performers': './/span[@class="tour_update_models"]/a/text()',
        'type': 'Scene',
        'external_id': r'.*/(.*?)$',
        'pagination': '/categories/movies_%s.html',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            item = self.init_scene()
            item['title'] = self.get_title(scene)
            item['image'] = scene.xpath('.//video/@poster_4x|.//img/@src0_4x').get()
            item['image'] = self.format_link(response, item['image'])

            if 'image' not in item or not item['image']:
                item['image'] = None
                item['image_blob'] = None
            else:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            if 'image_blob' not in item:
                item['image'] = None
                item['image_blob'] = None

            if item['image']:
                if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

            item['performers'] = self.get_performers(scene)
            item['tags'] = ['Gay']
            item['id'] = re.search(r'.*/(\d+)-', item['image']).group(1)

            sceneurl = scene.xpath('./a[1]/@href').get()
            item['url'] = self.format_link(response, sceneurl)

            item['network'] = 'Cum Here Boy'
            item['parent'] = 'Cum Here Boy'
            item['site'] = 'Cum Here Boy'
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
