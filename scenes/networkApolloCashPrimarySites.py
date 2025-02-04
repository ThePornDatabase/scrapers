import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkApolloCashPrimarySitesSpider(BaseSceneScraper):
    name = 'ApolloCashPrimarySites'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.missdp.com',
        'https://www.luckyamateurs.com',
        'https://www.turbomoms.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/index.php?updates=1&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1/ancestor::table[1]/ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h1/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('.//td[@width="881"]/font/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())

            tags = scene.xpath('.//b[contains(text(), "Tags:")]/following-sibling::text()[1]')
            if tags:
                tags = tags.get()
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.split(",")))

            performers = scene.xpath('.//td[@align="center"]/font/b/text()')
            if performers:
                performers = performers.get()
                performers = performers.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                if performers:
                    if "(" in performers:
                        performers = re.search(r'(.*) \(', performers).group(1)
                    item['performers'] = [performers]

            image = scene.xpath('.//img[contains(@src, "screenshot")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_screen', item['image']).group(1)
                if ".com" in item['id'].lower():
                    item['id'] = re.search(r'\.com_(.*)', item['id'].lower()).group(1)

            item['site'] = self.get_site(response)
            item['parent'] = self.get_site(response)
            item['network'] = "Apollo Cash"
            item['url'] = response.url

            yield item
