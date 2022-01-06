import re
import json
from datetime import date, timedelta
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
        item['image_blob'] = None
        item['trailer'] = ''
        item['url'] = jsondata['video']['url']
        item['id'] = re.search(r'videos/(.*)', item['url']).group(1)
        item['date'] = self.parse_date(jsondata['video']['datePublished'].strip()).isoformat()
        item['site'] = "Virtual Taboo"
        item['parent'] = "POVR"
        item['network'] = "POVR"

        item['tags'] = jsondata['video']['keywords']
        tags2 = item['tags'].copy()
        for tag in tags2:
            if re.match(r'\d+K', tag):
                item['tags'].remove(tag)
        item['tags'] = list(map(lambda x: x.strip().title(), set(item['tags'])))

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filterdate:
                item['filtered'] = "Scene filtered due to date restraint"
            print(item)
        else:
            if filterdate:
                if item['date'] > filterdate:
                    yield item
            else:
                yield item
