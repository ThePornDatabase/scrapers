import re
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBralessForeverSpider(BaseSceneScraper):
    name = 'BralessForever'

    start_urls = [
        'https://app.bralessforever.com',
    ]

    selector_map = {
        'external_id': r'videos/(.*)',
        'pagination': '/browse/videos?channel_visibility=%%22ALL%%22&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h3/ancestor::a[1][contains(@href, "video")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[contains(@type,"ld+json")]/text()').get()
        jsondata = json.loads(jsondata)
        item = self.init_scene()

        item['title'] = self.cleanup_title(jsondata['name'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', jsondata['uploadDate']).group(1)
        if "description" in jsondata and jsondata['description']:
            item['description'] = self.cleanup_description(jsondata['description'])

        if "image" in jsondata and jsondata['image']:
            item['image'] = jsondata['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['url'] = jsondata['contentUrl']
        item['id'] = re.search(r'videos/(.*)', response.url).group(1)

        if "duration" in jsondata and jsondata['duration']:
            item['duration'] = re.search(r'(\d+)', jsondata['duration']).group(1)

        item['performers'] = []
        if "actor" in jsondata and jsondata['actor']:
            for actor in jsondata['actor']:
                item['performers'].append(string.capwords(actor['name']))

            item['performers_data'] = self.get_performers_data(response)

        item['site'] = "Braless Forever"
        item['parent'] = "Braless Forever"
        item['network'] = "Braless Forever"

        yield self.check_item(item, self.days)

    def get_performers_data(self, response):
        performers = response.xpath('//a[contains(@class,"hover:text-white") and contains(@href, "users")]')
        if performers:
            performers_data = []
            for performer in performers:
                perf = {}
                perf['name'] = performer.xpath('.//div[contains(@class, "text-bold")]/text()').get()
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Braless Forever"
                perf['site'] = "Braless Forever"
                image = performer.xpath('.//img/@src')
                if image:
                    image = image.get()
                    if "avatar" in image:
                        perf['image'] = image
                        perf['image_blob'] = self.get_image_blob_from_link(image)
                performers_data.append(perf)
        return performers_data
