import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRGoddessSpider(BaseSceneScraper):
    name = 'VRGoddess'

    start_urls = [
        'https://www.vrgoddess.com'
    ]

    selector_map = {
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateThumb"]//img[contains(@class, "stdimage")]/ancestor::div[@class="updateItem"]')
        for scene in scenes:
            item = self.init_scene()
            item['site'] = "VRGoddess"
            item['parent'] = "VRGoddess"
            item['network'] = "NebraskaCoeds"
            item['type'] = "Scene"
            item['title'] = self.cleanup_description(scene.xpath('.//h5/a/text()').get())
            item['date'] = self.parse_date(scene.xpath('.//span[@class="availdate"]/text()').get(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            performers = scene.xpath('.//span[@class="tour_update_models"]/a/text()').getall()
            item['performers'] = []
            item['performers_data'] = []
            for performer in performers:
                performer = string.capwords(performer.strip())
                performer_extra = {}
                performer_extra['name'] = performer
                performer_extra['site'] = "NebraskaCoeds"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = "Female"
                item['performers_data'].append(performer_extra)
                item['performers'].append(performer)
            image = scene.xpath('.//img/@src0_3x')
            if image:
                image = image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
            sceneid = scene.xpath('.//img/@alt')
            if sceneid:
                sceneid = sceneid.get()
                item['id'] = re.search(r'^(\d+)', sceneid).group(1)
                sceneurl = re.search(r'^\d+_(.*)', sceneid).group(1)
                sceneurl = sceneurl.replace("_", "-")
                item['url'] = "https://www.vrgoddess.com/trailers/" + sceneurl
            item['tags'] = ["Virtual Reality"]

            yield self.check_item(item, self.days)
