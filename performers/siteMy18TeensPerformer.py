import string
import base64

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem
from tpdb.helpers.http import Http


class SiteMy18TeensPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': "",
        'pagination': '/models?page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'My18TeensPerformer'
    network = "My 18 Teens"

    start_urls = [
        'https://www.my18teens.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[contains(@class, "actor-preview")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//span[contains(@class, "name")]/text()').get()
            if name:
                item['name'] = string.capwords(name)
            else:
                item['name'] = ''

            image = performer.xpath('./div/@data-lazy-bgr').get()
            if image:
                item['image'] = self.format_link(response, image.strip())
                item['image_blob'] = self.get_image_blob(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None

            url = performer.xpath('./@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'My 18 Teens'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item

    def get_image_blob(self, image):
        if image:
            req = Http.get(image, headers=self.headers, cookies=self.cookies)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None
