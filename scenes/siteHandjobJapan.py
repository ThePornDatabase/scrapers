import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHandjobJapanSpider(BaseSceneScraper):
    name = 'HandjobJapan'
    site = 'Handjob Japan'
    parent = 'Handjob Japan'
    network = 'Handjob Japan'

    start_urls = [
        'https://www.handjobjapan.com',
    ]

    max_pages = 23

    selector_map = {
        'title': './following-sibling::div[contains(@class, "blurb")][1]/text()',
        'description': './following-sibling::div[contains(@class, "blurb")][1]/text()',
        'date': '',
        'image': './following-sibling::div[contains(@class, "player")][1]/@style',
        're_image': r'(http.*?)\)',
        'performers': './div[contains(@class, "ltitle")]/h1/text()',
        'tags': '',
        'duration': './div[contains(@class, "rtitle")]/h3[1]/strong/text()',
        'trailer': './following-sibling::div[contains(@class, "player")][1]//source/@src',
        'external_id': r'',
        'pagination': '/en/samples?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item-title"]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['image'] = scene.xpath('./following-sibling::div[contains(@class, "player")][1]/@style').get()
            item['image'] = re.search(r'(http.*?)\)', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(scene)
            item['performers_data'] = self.get_performers_data(scene)
            item['tags'] = ['Asian', 'Handjob']
            item['duration'] = self.get_duration(scene)
            item['trailer'] = scene.xpath('./following-sibling::div[contains(@class, "player")][1]//source/@src').get()
            item['site'] = "Handjob Japan"
            item['parent'] = "Handjob Japan"
            item['network'] = "Handjob Japan"
            item['type'] = "Scene"
            item['id'] = re.search(r'.*/(.*?)/', item['image']).group(1)
            item['url'] = f"https://www.handjobjapan.com/en/video/{item['id']}"

            yield item

    def get_performers(self, scene):
        performers = scene.xpath('./div[contains(@class, "ltitle")]/h1/text()')
        if performers:
            performers = performers.get()
            if "," in performers:
                performers = performers.split(",")
                return list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                return [string.capwords(performers.strip())]
        return []

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['extra']['ethnicity'] = "Asian"
                perf['network'] = "Handjob Japan"
                perf['site'] = "Handjob Japan"
                performers_data.append(perf)
        return performers_data
