import re
import html
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkBangNewSpider(BaseSceneScraper):
    name = 'BangNew'
    network = 'Bang'
    parent = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    selector_map = {
        'tags': '//div[@class="actions"]/a/text()',
        'trailer': '//div[@class="preview-holder"]//source[contains(@type, "mp4")]/@src',
        'external_id': r'video/(.*)/',

        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        link = f"/videos?from=bang%21+originals&page={page}"
        return self.format_url(base, link)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//li[@class="relative"]')
        for scene in scenes:
            meta['id'] = scene.xpath('./@data-video-id').get()
            scene = scene.xpath('./div/div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

        item['id'] = meta['id']

        jsondata = response.xpath('//script[contains(text(), "@id")]/text()').get()
        jsondata = json.loads(jsondata)

        item['title'] = html.unescape(jsondata['name'])
        if jsondata['contentUrl']:
            item['image'] = jsondata['contentUrl']
        else:
            item['image'] = jsondata['thumbnailUrl']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['description'] = html.unescape(jsondata['description'])
        item['date'] = self.parse_date(jsondata['datePublished']).isoformat()
        item['performers'] = []
        for model in jsondata['actor']:
            item['performers'].append(html.unescape(model['name']))

        item['duration'] = self.convert_duration(jsondata['duration'])
        item['tags'] = self.get_tags(response)
        item['trailer'] = self.get_trailer(response)
        item['director'] = ''

        item['site'] = response.xpath('//div[@data-login-target="expandParagraph"]//a[contains(@href, "/videos?in")]/text()').get()
        if not item['site']:
            item['site'] = "Bang! Originals"
        item['site'] = self.cleanup_title(item['site'].replace("\n", "").replace("\r", "").replace("\t", "").strip())

        item['parent'] = "Bang"
        item['network'] = "Bang"
        item['url'] = response.url
        yield self.check_item(item, self.days)

    def convert_duration(self, duration):
        if "PT" in duration:
            duration = duration.replace(":", "")
            if "H" in duration:
                duration = re.search(r'(\d{1,2})H(\d{1,2})M(\d{1,2})S', duration)
                hours = int(duration.group(1)) * 3600
                minutes = int(duration.group(2)) * 60
                seconds = int(duration.group(3))
                duration = str(hours + minutes + seconds)
            else:
                duration = re.search(r'(\d{1,2})M(\d{1,2})S', duration)
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                duration = str(minutes + seconds)
            return duration
        return ''
