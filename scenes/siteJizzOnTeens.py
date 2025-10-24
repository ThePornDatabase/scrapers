import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJizzOnTeensSpider(BaseSceneScraper):
    name = 'JizzOnTeens'
    network = 'Jizz On Teens'
    parent = 'Jizz On Teens'
    site = 'Jizz On Teens'

    start_urls = [
        'http://www.jizzonteens.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="box-outer"][.//h2]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h2/text()').get()
            item['title'] = string.capwords(self.cleanup_title(title))

            description = scene.xpath('.//p/textarea/text()')
            if description:
                item['description'] = description.get()

            image = scene.xpath('.//video/@poster')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'content/(.*?)/', image).group(1)
            item['url'] = response.url
            item['site'] = "Jizz On Teens"
            item['parent'] = "Jizz On Teens"
            item['network'] = "Jizz On Teens"

            if item['id']:
                yield item
