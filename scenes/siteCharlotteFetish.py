import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCharlotteFetishSpider(BaseSceneScraper):
    name = 'CharlotteFetish'
    network = 'CharlotteFetish'
    parent = 'CharlotteFetish'
    site = 'CharlotteFetish'

    start_urls = [
        'https://www.charlottefetish.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/preview.php?view_mode=detail&id=0',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 21)
        pagination = '/preview.php?view_mode=detail&id=%s'
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//table[@width="710"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//td[contains(@width, "88")]//a[contains(@class, "preview_header")]/text()')
            if title:
                title = title.get()
                title = self.cleanup_title(title).strip()
                item['title'] = string.capwords(title)

            description = scene.xpath('.//td[contains(@width, "88")]//a[contains(@class, "preview_header")]/ancestor::div[1]/following-sibling::div[1]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get().strip())

            image = scene.xpath('.//td[contains(@width, "88")]//a[contains(@class, "preview_header")]/ancestor::table[1]/ancestor::table[1]/ancestor::table[1]//td[contains(@width, "12")]//img/@src')
            if image:
                image = image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

            item['url'] = self.format_link(response, scene.xpath('.//td[contains(@width, "88")]//a[contains(@class, "preview_header")]/@href').get())
            item['id'] = re.search(r'=(\d+)', item['url'])
            if item['id']:
                item['id'] = item['id'].group(1)

            item['performers'] = ["Charlotte Brook"]
            item['tags'] = ['Bondage']

            item['site'] = "CharlotteFetish"
            item['parent'] = "CharlotteFetish"
            item['network'] = "CharlotteFetish"

            if item['id']:
                yield item
