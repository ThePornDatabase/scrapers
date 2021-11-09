import re
import string
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotWifeRioSpider(BaseSceneScraper):
    name = 'HotWifeRio'
    network = 'Hot Wife Rio'

    start_urls = [
        'https://hotwiferio.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/new-tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('./div/span[@class="update_title"]/text()')
            item['title'] = ''
            if title:
                item['title'] = string.capwords(title.get().strip())

            description = scene.xpath('.//span[@class="update_description"]/text()')
            item['description'] = ''
            if description:
                item['description'] = description.get().strip()

            scenedate = scene.xpath('.//span[@class="update_date"]/text()')
            item['date'] = dateparser.parse('today').isoformat()
            if scenedate:
                item['date'] = dateparser.parse(scenedate.get().strip(), date_formats=['%m/%d/%Y']).isoformat()

            image = scene.xpath('./following-sibling::div[@class="update_image"]/img/@src')
            item['image'] = ''
            if image:
                item['image'] = "https://hotwiferio.com/new-tour/" + image.get().strip()

            item['performers'] = ['Rio Blaze']

            tags = scene.xpath('.//span[@class="update_tags"]/a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))

            item['url'] = response.url
            item['site'] = "Hot Wife Rio"
            item['parent'] = "Hot Wife Rio"
            item['network'] = "Hot Wife Rio"

            item['trailer'] = ''

            item['id'] = ''
            externid = re.search(r'content/(.*?)/', item['image'])
            if externid:
                item['id'] = externid.group(1).strip()

            if item['id'] and item['title']:
                yield item
