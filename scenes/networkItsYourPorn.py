import re
import base64
from tpdb.helpers.http import Http
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
false = False
true = True


class NetworkItsYourPornSpider(BaseSceneScraper):
    name = 'ItsYourPorn'

    start_urls = [
        'https://members.itsyourporn.com',
    ]

    selector_map = {
        'title': './/h1/text()',
        'description': './/li[@class="description"]/p/text()',
        'date': './/label[contains(text(), "Date Added")]/span/text()',
        'image': './/div[@class="scene-thumb"]/a/img/@src',
        'performers': './/ul[@class="scene-selections"]//li/a[contains(@href, "model_id")]/text()',
        'tags': './/ul[@class="scene-selections"]//li/a[contains(@href, "category_id")]/text()',
        'duration': './/label[@class="length"]/span[contains(text(), "min")]/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/movies.php?p=%s',
        'type': 'Scene',
    }

    cookies = []

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene"]|//div[@class="scene end"]')
        for scene in scenes:
            item = SceneItem()
            item['type'] = "Scene"

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            item['image'] = self.get_image(scene)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = None
            item['duration'] = self.get_duration(scene)
            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)
            item['trailer'] = None
            item['url'] = "https://members.itsyourporn.com/" + scene.xpath('.//div[contains(@class, "scene-thumb")]/a/@href').get()
            sceneid = scene.xpath('.//div[contains(@class, "scene-thumb")]/a/@href').get()
            item['id'] = re.search(r'id=(\d+)', sceneid).group(1)
            item['network'] = "Its Your Porn"
            item['parent'] = scene.xpath('.//label[@class="site"]//a/text()').get()
            item['site'] = scene.xpath('.//label[@class="site"]//a/text()').get()
            yield self.check_item(item, self.days)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = response.xpath(self.get_selector_map('image'))
            if image:
                image = image.get()
                image = re.search(r'(.*?)\?', image).group(1)
                image = image.replace(' ', '%20')
                return image
        return ''

    def get_image_blob_from_link(self, image):
        if image:
            req = Http.get(image, headers=self.headers, verify=False)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            duration = re.search(r'(\d+) min', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return None
