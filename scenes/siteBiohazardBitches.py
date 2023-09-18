import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBiohazardBitchesSpider(BaseSceneScraper):
    name = 'BiohazardBitches'

    start_urls = [
        'http://www.biohazardbitches.com',
    ]

    selector_map = {
        'title': './/div[@class="videotitle"]/text()',
        'description': './/div[@class="description"]/text()',
        'image': './/td[@class="video"]//img/@src',
        'performers': './/div[@class="videotitle"]/text()',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/page%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//table[@class="videobox"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.get_title(scene)
            item['date'] = self.get_date(scene)
            item['description'] = self.get_description(scene)
            item['image'] = self.get_image(scene, response.url)
            item['image'] = item['image'].replace(".jpg", "/01.jpg")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)
            item['trailer'] = self.get_trailer(scene, response.url)
            item['type'] = 'Scene'
            item['duration'] = None
            item['url'] = self.format_link(response, scene.xpath('.//td[@class="video"]/a/@href').get())
            item['id'] = re.search(r'.*/(.*?)\.htm', item['url']).group(1)
            item['site'] = "Biohazard Bitches"
            item['parent'] = "Biohazard Bitches"
            item['network'] = "Biohazard Bitches"
            yield item
            # ~ print(item)
