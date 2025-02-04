import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkApolloCashFaceExclusiveClubSpider(BaseSceneScraper):
    name = 'ApolloCashExclusiveClub'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.exclusiveclub.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=1&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1/ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h1/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('.//b[contains(text(), "Count of")]/ancestor::td[1]/font[1]/text()')
            if description:
                description = description.getall()
                description = "".join(description)
                item['description'] = self.cleanup_description(description.strip())

            tags = scene.xpath('.//img[contains(@alt, "Tags")]/@alt')
            if tags:
                tags = tags.get()
                tags = re.search(r'Tags:(.*)', tags).group(1)
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.split(",")))

            performers = scene.xpath('.//b[contains(text(), "Patient name")]/../following-sibling::font[contains(text(), "(")][1]/text()')
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

            image = scene.xpath('.//img[contains(@alt, "Tags")]/@src')
            if not image:
                image = scene.xpath('.//img[contains(@src, "ExclusiveClub.com")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_free', item['image']).group(1)
                if ".com" in item['id'].lower():
                    item['id'] = re.search(r'\.com_(.*)', item['id'].lower()).group(1)

            item['site'] = "Exclusive Club"
            item['parent'] = "Exclusive Club"
            item['network'] = "Apollo Cash"
            item['url'] = response.url

            yield item
