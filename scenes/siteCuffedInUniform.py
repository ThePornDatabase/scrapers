import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCuffedInUniformSpider(BaseSceneScraper):
    name = 'CuffedInUniform'
    network = 'Cuffed In Uniform'
    parent = 'Cuffed In Uniform'
    site = 'Cuffed In Uniform'

    start_urls = [
        'https://www.cuffedinuniform.com',
    ]

    selector_map = {
        'title': './/h2/a/text()',
        'description': './/div[contains(@class, "entry-content-excerpt")]/p//text()',
        'date': './/h2/following-sibling::div[contains(@class, "entry-meta")][1]/text()[contains(., "Model")][1]',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'performers': './/h2/following-sibling::div[contains(@class, "entry-meta")][1]//a[contains(@href, "/tag/")]/text()',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.get_title(scene)
            if " - " in item['title']:
                item['title'] = re.search(r' - (.*)', item['title']).group(1)
            item['description'] = self.get_description(scene).replace("\n", " ").replace("\r", "").replace("\t", "")
            item['date'] = self.get_date(scene)

            item['image'] = scene.xpath('.//figure//img/@src')
            if item['image']:
                item['image'] = item['image'].get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            item['performers'] = self.get_performers(scene)
            item['tags'] = ['Bondage', 'Uniform']
            item['site'] = "Cuffed In Uniform"
            item['parent'] = "Cuffed In Uniform"
            item['network'] = "Cuffed In Uniform"
            item['type'] = "Scene"

            sceneid = scene.xpath('.//h2/following-sibling::div[contains(@class, "entry-meta")][1]/text()[contains(., "Model")][1]')
            if sceneid:
                sceneid = re.search(r'(CIU\d+)', sceneid.get())
                if sceneid:
                    item['id'] = sceneid.group(1)
            item['url'] = scene.xpath('.//h2/a/@href').get()

            yield item
