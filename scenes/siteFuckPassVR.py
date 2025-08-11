import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFuckpassVRSpider(BaseSceneScraper):
    name = 'FuckPassVR'
    network = 'FuckPassVR'
    parent = 'FuckPassVR'
    site = 'FuckPassVR'

    start_urls = [
        'https://www.fuckpassvr.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[contains(@class, "readMoreWrapper2")]/p//text()',
        'date': '//span[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%b %d %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Starring")]/following-sibling::a/span/text()',
        'tags': '//span[contains(text(), "Tags")]/following-sibling::a/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)$',
        'pagination': '/destination?page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoInfo")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags.append("Virtual Reality")
        specs = response.xpath('//span[contains(text(), "Specs")]/following-sibling::text()')
        if specs:
            specs = specs.get()
            specs = specs.split(",")
            for spec in specs:
                tags.append(spec.strip())
        return tags

    def get_image(self, response):
        image = response.xpath('//pornhall-player/@poster')
        if image:
            image = image.get()
            if "'" in image:
                image = image.replace("'", "")
            return image

    def parse_scene(self, response):
        item = self.init_scene()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None
            item['image_blob'] = None
        else:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if 'image_blob' not in item:
            item['image'] = None
            item['image_blob'] = None

        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['type'] = 'Scene'
        if "check_date" in response.meta and item['date'] > "2024-06-07":
            check_date = response.meta['check_date']
            if item['date'] > check_date:
                yield self.check_item(item, self.days)
        else:
            yield self.check_item(item, self.days)
