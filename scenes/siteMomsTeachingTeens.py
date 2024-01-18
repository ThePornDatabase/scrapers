import re
import scrapy
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMomsTeachingTeensSpider(BaseSceneScraper):
    name = 'MomsTeachingTeens'
    network = 'MomsTeachingTeens'
    parent = 'MomsTeachingTeens'
    site = 'MomsTeachingTeens'

    start_urls = [
        'http://momsteachingteens.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//comment()[contains(., "START EPISODE")]/following-sibling::tr[2]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//h1/text()').get())
            description = scene.xpath('./preceding-sibling::comment()/following-sibling::tr//div[@id="desc"]/text()').getall()
            description = " ".join(description)
            item['description'] = self.cleanup_description(description)
            item['date'] = ""
            item['image'] = self.format_link(response, scene.xpath('.//h1/following-sibling::table//img[contains(@src, "teen")]/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = []
            item['tags'] = ['Family Roleplay']
            item['duration'] = None
            item['trailer'] = ""
            item['id'] = slugify(re.sub('[^a-z0-9- ]', '', item['title'].lower().strip()))
            item['url'] = f"http://momsteachingteens.com/{item['id']}"
            item['site'] = "MomsTeachingTeens"
            item['parent'] = "MomsTeachingTeens"
            item['network'] = "MomsTeachingTeens"
            item['type'] = "Scene"
            yield self.check_item(item, self.days)
