import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHeavyChainsSpider(BaseSceneScraper):
    name = 'HeavyChains'
    network = 'Heavy Chains'
    parent = 'Heavy Chains'
    site = 'Heavy Chains'

    start_urls = [
        'https://www.heavy-chains.com',
    ]

    selector_map = {
        'description': '',
        'performers': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="collection"]')
        for scene in scenes:
            item = self.init_scene()

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::span[1]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                if scenedate:
                    item['date'] = scenedate.group(1)

            if self.check_item(item, self.days):

                title = scene.xpath('.//h2/a/text()')
                if title:
                    title = title.get()
                    item['title'] = self.cleanup_title(title)

                image = scene.xpath('.//div[@class="preview-theme"]/div[1]/div[1]/a[contains(@href, ".jpg")]/@href')
                if image:
                    image = image.get()
                    image = self.format_link(response, image)
                    item['image'] = re.search(r'(.*)\?', image).group(1)
                    item['image_blob'] = self.get_image_blob_from_link(image)

                    item['id'] = re.search(r'collections/(.*?)/', image).group(1)

                tags = scene.xpath('.//span[@title="Categories"]/span/a/text()')
                if tags:
                    item['tags'] = tags.getall()
                    item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))

                duration = scene.xpath('.//span[contains(@class, "fa5-text") and contains(text(), "minutes")]/text()')
                if duration:
                    duration = duration.get()
                    duration = re.search(r'((?:\d{1,2}\:)?\d{1,2}\:\d{2})', duration)
                    if duration:
                        item['duration'] = self.duration_to_seconds(duration.group(1))

                item['url'] = self.format_link(response, scene.xpath('.//h2/a/@href').get())

                item['site'] = "Heavy Chains"
                item['network'] = "Heavy Chains"
                item['parent'] = "Heavy Chains"

                yield item
