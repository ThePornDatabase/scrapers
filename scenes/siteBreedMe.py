import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBreedMeSpider(BaseSceneScraper):
    name = 'BreedMe'
    network = 'TugPass'
    parent = 'Breed Me'
    site = 'Breed Me'

    start_urls = [
        'https://www.breedme.com',
    ]

    selector_map = {
        'title': './/h3/text()',
        'description': './/p/text()',
        'date': './/span[contains(text(), "Date:")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': './/img/@src',
        'performers': './/a[contains(@href, "/models/")]/text()',
        'tags': '',
        'duration': './/span[contains(text(), "Video")]/text()',
        're_duration': r'(\d{1,2}:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos/%s.php',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update-box"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['date'] = self.get_date(scene)
            item['description'] = self.get_description(scene)
            item['image'] = self.get_image(scene, response.url)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)
            item['trailer'] = self.get_trailer(scene, response.url)
            item['type'] = 'Scene'
            item['duration'] = self.get_duration(scene)
            item['url'] = self.format_link(response, scene.xpath('./div[1]/a/@href').get())
            if "?nats" in item['url']:
                item['url'] = re.search(r'(.*)\?nats', item['url']).group(1)
            item['id'] = re.search(r'videos/(.*)\.htm', item['url']).group(1)
            item['site'] = "Breed Me"
            item['parent'] = "Breed Me"
            item['network'] = "TugPass"
            yield item
