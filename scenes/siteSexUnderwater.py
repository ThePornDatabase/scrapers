import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSexUnderwaterSpider(BaseSceneScraper):
    name = 'SexUnderwater'
    network = 'Sex Underwater'
    parent = 'Sex Underwater'
    site = 'Sex Underwater'

    start_urls = [
        'https://sexunderwater.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_text(scene.xpath('.//h4/a/text()').get())
            scenedate = scene.xpath('.//p/span[not(contains(@class, "models"))]/text()').get()
            item['description'] = ''
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            performers = scene.xpath('.//p/span[contains(@class, "update_models")]/a/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            trailer = scene.xpath('./a/@onclick').get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*?)\'\)', trailer)
                trailer = trailer.group(1)
                item['trailer'] = self.format_link(response, trailer.replace(" ", "%20"))
            else:
                item['trailer'] = ''
            image = scene.xpath('./a/img/@src0_3x').get()
            item['tags'] = ['Underwater']
            item['image'] = self.format_link(response, image).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            sceneid = re.search('content/(.*?)/', item['image'])
            if sceneid:
                item['id'] = sceneid.group(1)
            item['url'] = response.url
            item['site'] = 'Sex Underwater'
            item['parent'] = 'Sex Underwater'
            item['network'] = 'Sex Underwater'

            yield self.check_item(item, self.days)
