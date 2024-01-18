import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteOgresWorldSpider(BaseSceneScraper):
    name = 'OgresWorld'
    network = 'Ogres World'
    parent = 'Ogres World'
    site = 'Ogres World'

    start_urls = [
        'https://ogres-world.com',
    ]

    selector_map = {
        'title': './/h4/text()',
        'description': './/p[contains(@class, "setdesc")]/text()',
        'image': './/img/@src',
        'duration': './/p[contains(text(), "ideo")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'setid=(\d+)',
        'pagination': '/x-new/new-preview-grid.php?page=%s&user=ogres-world.com',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[contains(@class, "prevgrid")]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.get_title(scene)
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
            item['id'] = re.search(r'setid=(\d+)', item['url']).group(1)

            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['description'] = self.get_description(scene)
            item['date'] = ''
            item['performers'] = ['Vivienne Velvet']
            item['tags'] = ['Bondage']
            item['duration'] = self.get_duration(scene)
            item['type'] = 'Scene'
            item['trailer'] = ''
            item['site'] = 'Ogres World'
            item['parent'] = 'Ogres World'
            item['network'] = 'Ogres World'

            yield item

    def get_duration(self, response):
        duration = response.xpath('//p[contains(text(), "ideo")]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'((?:\d{1,2}\:)?\d{1,2}\:\d{2})', duration)
            if duration:
                duration = duration.group(1)
                return self.duration_to_seconds(duration)
        return None
