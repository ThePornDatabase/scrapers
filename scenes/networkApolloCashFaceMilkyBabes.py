import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkApolloCashMilkyBabesSpider(BaseSceneScraper):
    name = 'ApolloCashMilkyBabes'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.milkybabes.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=1&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//b[contains(text(), "Video Formats")]/ancestor::table[1]/ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//td[@align="left"]/a[1]/img[1]/@alt')
            if not title:
                title = scene.xpath('.//b[contains(text(), "Girl") and contains(text(), "name")]/following-sibling::text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            performers = scene.xpath('.//b[contains(text(), "Girl") and contains(text(), "name")]/following-sibling::text()')
            if performers:
                performers = performers.getall()
                performers = "".join(performers)
                performers = performers.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                if performers:
                    if "(" in performers:
                        performers = re.search(r'(.*)\(', performers).group(1)
                    item['performers'] = [performers]

            item['performers_data'] = []
            for performer in item['performers']:
                performer_extra = {}
                performer_extra['name'] = performer
                performer_extra['site'] = "Apollo Cash"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = "Female"
                item['performers_data'].append(performer_extra)

            image = scene.xpath('.//td[@align="left"]/a[1]/img[1]/@src')
            if not image:
                image = scene.xpath('.//img[contains(@src, "MilkyBabes.com")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_free', item['image']).group(1)
                if ".com" in item['id'].lower():
                    item['id'] = re.search(r'\.com_(.*)', item['id'].lower()).group(1)

            item['site'] = "Milky Babes"
            item['parent'] = "Milky Babes"
            item['network'] = "Apollo Cash"
            item['url'] = response.url

            yield item
