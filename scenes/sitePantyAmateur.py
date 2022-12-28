import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePantyAmateurSpider(BaseSceneScraper):
    name = 'PantyAmateur'
    network = 'Panty Amateur'
    parent = 'Panty Amateur'
    site = 'Panty Amateur'

    start_urls = [
        'https://www.pantyamateur.com',
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
        'pagination': '/?videos&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"itemmain")]')
        for scene in scenes:
            item = SceneItem()
            item['url'] = self.format_link(response, scene.xpath('./div/a/@href').get())
            item['title'] = self.cleanup_title(scene.xpath('.//div[contains(@class,"nm-name")]/p/text()').get())
            scenedate = scene.xpath('.//div[contains(@class,"nm-name")]/span/following-sibling::text()[contains(., "Added")]').get()
            scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            item['tags'] = scene.xpath('.//div[contains(@class,"nm-name")]/span/a/text()').getall()
            item['performers'] = [item['title']]
            duration = scene.xpath('.//div[contains(@class,"nm-name")]/span[contains(text(), "min")]/text()').get()
            duration = re.search(r'(\d+)\.(\d+)min', duration)
            if duration:
                item['duration'] = str((int(duration.group(1)) * 60) + int(duration.group(2)))
            else:
                item['duration'] = ''
            item['id'] = re.search(r'lid=(\d+)', item['url']).group(1)
            item['description'] = ''
            item['trailer'] = ''
            item['image'] = f"https://www.pantyamateur.com/preview/{item['id']}/big1.jpg"
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['site'] = 'Panty Amateur'
            item['parent'] = 'Panty Amateur'
            item['network'] = 'Panty Amateur'
            item['type'] = 'Scene'
            yield self.check_item(item, self.days)
