import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBondageJunkiesSpider(BaseSceneScraper):
    name = 'BondageJunkies'
    network = 'Bondage Junkies'
    parent = 'Bondage Junkies'
    site = 'Bondage Junkies'

    start_urls = [
        'https://bondagejunkies.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/updates?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1[contains(@class, "updatetitle")]/ancestor::div[2]')
        for scene in scenes:
            item = self.init_scene()
            title = scene.xpath('.//h1[contains(@class, "updatetitle")]/text()')
            if title:
                item['title'] = self.cleanup_title(title.get().strip())

            datetext = scene.xpath('.//p[@class="byliner"]/text()').getall()
            datetext = "".join(datetext)
            item['id'] = re.search(r'\#(\d+)', datetext).group(1)
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', datetext).group(1)
            datetext = re.sub(r'[^a-z0-9]+', '', datetext.lower())
            duration = re.search(r'(\d+)min', datetext)
            if duration:
                item['duration'] = str(int(duration.group(1)) * 60)

            description = scene.xpath('.//p[@class="updatedesc"]/text()')
            if description:
                description = description.getall()
                item['description'] = " ".join(description)

            tags = scene.xpath('.//p[@class="titletags"]/a/text()')
            if tags:
                tags = tags.getall()
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

            image = scene.xpath('.//img[contains(@src, "-lg-1")]/@src')
            if not image:
                image = scene.xpath('.//img[contains(@src, "-lg-2")]/@src')

            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['site'] = "Bondage Junkies"
            item['parent'] = "Bondage Junkies"
            item['network'] = "Bondage Junkies"

            yield self.check_item(item, self.days)
