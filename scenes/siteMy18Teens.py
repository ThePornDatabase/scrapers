import re
import string
import base64

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from tpdb.helpers.http import Http


class SiteMy18TeensSpider(BaseSceneScraper):
    name = 'My18Teens'
    network = 'My 18 Teens'
    parent = 'My 18 Teens'
    site = 'My 18 Teens'

    start_urls = [
        'https://www.my18teens.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)$',
        'trailer': '',
        'pagination': '/new?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "video-preview_full videos__item")]')
        for scene in scenes:
            item = SceneItem()

            titledate = scene.xpath('./div[contains(@class, "video-preview__data")]/p[contains(@class, "title")]/text()')
            if titledate:
                titledate = titledate.get()
                if re.search(r'(\d{2}\.\d{2}\.\d{4})', titledate):
                    item['date'] = self.parse_date(re.search(r'(\d{2}\.\d{2}\.\d{4})', titledate).group(1), date_formats=['%d.%m.%Y']).isoformat()
                else:
                    item['date'] = self.parse_date('today').isoformat()
                item['title'] = string.capwords(titledate)
            else:
                item['title'] = ''
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('./div[contains(@class, "video-preview__data")]/div[contains(@class, "actors")]/span/text()')
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers.getall()))
            else:
                item['performers'] = []

            item['tags'] = ['Teen']
            if len(item['performers']) > 1:
                item['tags'].append('Lesbian')
                item['tags'].append('Toys')

            item['trailer'] = ''
            item['description'] = ''

            image = scene.xpath('./div[contains(@class, "video-preview__image")]/@data-lazy-bgr')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None
            item['url'] = self.format_link(response, scene.xpath('./@href').get())
            item['id'] = re.search(r'.*/(.*?)$', item['url']).group(1)
            item['network'] = "My 18 Teens"
            item['parent'] = "My 18 Teens"
            item['site'] = "My 18 Teens"

            yield item

    def get_image_blob(self, image):
        if image:
            req = Http.get(image, headers=self.headers, cookies=self.cookies)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None
