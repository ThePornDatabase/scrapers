import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class siteDawgpoundUSASpider(BaseSceneScraper):
    name = 'DawgpoundUSA'
    network = 'DawgpoundUSA'
    parent = 'DawgpoundUSA'
    site = 'DawgpoundUSA'

    start_urls = [
        'https://dawgpoundusa.com',
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
        'pagination': '/dawgPoundCinema.cfm?PAGE=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "item")]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('.//h4/span/text()')
            if not title:
                title = scene.xpath('.//text()[contains(., "in ")]')
                if title:
                    title = re.search(r'in (.*)', title.get()).group(1)
            else:
                title = title.get()

            item['title'] = self.cleanup_title(title)
            item['description'] = self.cleanup_description(scene.xpath('.//input[@type="image"]/@alt').get())
            item['date'] = ""
            item['image'] = scene.xpath('.//input[@type="image"]/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene.xpath('.//span[@itemprop="actors"]/a/span/text()').getall()
            item['tags'] = ['Gay', 'African American']
            item['duration'] = None
            item['trailer'] = None
            item['id'] = scene.xpath('.//input[@name="ClipID"]/@value').get()
            item['url'] = response.url
            item['site'] = 'DawgpoundUSA'
            item['parent'] = 'DawgpoundUSA'
            item['network'] = 'DawgpoundUSA'
            yield item
