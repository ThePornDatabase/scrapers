import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteClairesSlavesSpider(BaseSceneScraper):
    name = 'ClairesSlaves'

    start_urls = [
        'https://www.clairesslaves.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/updates.php?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//td[contains(text(), "video clip")]/ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//td[contains(text(), "video clip")]/strong/text()')
            if title:
                title = title.get()
                item['title'] = self.cleanup_title(title.strip())

            image = scene.xpath('.//img[contains(@src, "updates")]/@src')
            if image:
                image = image.get()
                image = image.replace("../", "")
                item['image'] = self.format_link(response, image.strip())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['url'] = response.url

            description = scene.xpath('.//p[not(contains(@align,"center"))]//text()')
            if description:
                description = description.getall()
                description = " ".join(description).replace("  ", " ").strip()
                item['description'] = self.cleanup_description(description)

            item['id'] = re.search(r'.*_(.*?)\.', item['image']).group(1)

            item['network'] = 'Claires Slaves'
            item['parent'] = 'Claires Slaves'
            item['site'] = 'Claires Slaves'

            yield item