import re
import html
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBangSpider(BaseSceneScraper):
    name = 'Bang'
    network = 'Bang'
    parent = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '//div[contains(@class, "actions")]/a[contains(@href, "with")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = f"https://www.bang.com/videos?from=bang%21+originals&page={page}"
        return pagination

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"video_preview_container")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()
        jsondata = response.xpath('//script[contains(@type, "json") and contains(text(), "duration")]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            item['title'] = jsondata['name']
            item['date'] = jsondata['datePublished']
            item['description'] = html.unescape(jsondata['description'])
            item['image'] = jsondata['thumbnailUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = jsondata['@id']
            item['type'] = 'Scene'
            item['url'] = response.url
            item['duration'] = self.duration_to_seconds(jsondata['duration'])
            item['performers'] = []
            for person in jsondata['actor']:
                item['performers'].append(person['name'])

            item['tags'] = self.get_tags(response)
            item['site'] = re.sub('[^a-zA-Z0-9-]', '', response.xpath('//p[contains(text(), "From the Movie")]/a[2]/text()').get())
            trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "mp4")]/@src')
            if not trailer:
                trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "webm")]/@src')
            if trailer:
                item['trailer'] = trailer.get()
            else:
                item['trailer'] = ''
            item['network'] = 'Bang'
            item['parent'] = 'Bang'

            yield self.check_item(item, self.days)
