import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteVirtualTabooSpider(BaseSceneScraper):
    name = 'VirtualTaboo'

    start_urls = [
        'https://virtualtaboo.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)',
        'trailer': '',
        'duration': '//div[contains(@class,"video-detail")]//div[contains(@class,"info")]/text()',
        're_duration': r'((?P<hour>[0-9]+) (?:hour[s]?\s*)?)?(?P<min>[0-9]+) min',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "video-card")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[contains(@type, "json")]').get()
        jsondata = re.search(r'(\{.*\})', jsondata).group(1)
        jsondata = json.loads(jsondata)
        item = SceneItem()

        item['performers'] = []
        for model in jsondata['video']['actor']:
            item['performers'].append(model['name'].title())

        item['title'] = self.cleanup_title(jsondata['video']['name'])
        item['description'] = self.cleanup_description(jsondata['video']['description'])
        if not item['description']:
            item['description'] = ''

        item['image'] = jsondata['video']['thumbnail']
        if not item['image']:
            item['image'] = None
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['trailer'] = ''
        item['url'] = jsondata['video']['url']
        item['id'] = re.search(r'videos/(.*)', item['url']).group(1)
        item['date'] = self.parse_date(jsondata['video']['datePublished'].strip()).isoformat()
        item['site'] = "Virtual Taboo"
        item['parent'] = "Virtual Taboo"
        item['network'] = "Virtual Taboo"

        item['tags'] = jsondata['video']['keywords']
        tags2 = item['tags'].copy()
        for tag in tags2:
            if re.match(r'\d+K', tag):
                item['tags'].remove(tag)
        item['tags'] = list(map(lambda x: x.strip().title(), set(item['tags'])))

        # Duration in jsondata is unreliable, grabbing from video info section
        item['duration'] = self.get_duration(response)

        yield self.check_item(item, self.days)

    def get_duration(self, response):
        selector = self.get_selector_map('duration')
        regexp, group, mod = self.get_regex(self.regex['re_duration'])
        info = self.process_xpath(response, selector)

        for text in info:
            match = regexp.search(text.get())
            if match:
                duration = int(match.group("min")) * 60
                if match.group("hour"):
                    duration += int(match.group("hour")) * 3600

                return duration
