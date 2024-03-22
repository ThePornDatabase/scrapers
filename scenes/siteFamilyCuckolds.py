import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFamilyCuckoldsSpider(BaseSceneScraper):
    name = 'FamilyCuckolds'

    start_url = 'https://familycuckolds.com/'

    selector_map = {
        'title': './/div[@class="name"]/span/text()',
        'description': '',
        'date': './/div[@class="date"]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': './following-sibling::script[1]/text()',
        're_image': r'show_poster.*?(http.*?)[\'\"]',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request('https://familycuckolds.com/', callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="episode-item"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.get_title(scene)
            item['description'] = ""
            item['site'] = "Family Cuckolds"
            item['date'] = self.get_date(scene)
            item['image'] = self.get_image(scene, response)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = []
            item['tags'] = ['Cuckold']
            sceneid = scene.xpath('./@id').get()
            item['id'] = re.search(r'(\d+)', sceneid).group(1)
            item['trailer'] = ""
            item['url'] = self.get_url(response) + "video/" + sceneid
            item['network'] = "Family Cuckolds"
            item['parent'] = "Family Cuckolds"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)

    def get_image(self, scene, response, path=None):
        if 'image' in self.get_selector_map():
            image = self.get_element(scene, 'image', 're_image')
            if isinstance(image, list):
                image = image[0]
            image = image.strip()
            image = image.replace(" ", "%20")
            return self.format_link(response, image)
        return ''
