import re
from datetime import date, timedelta
import json
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class BiGuysFuckSpider(BaseSceneScraper):
    name = 'BiGuysFuck'
    network = "Bi Guys Fuck"
    parent = "Bi Guys Fuck"

    start_urls = [
        'https://www.biguysfuck.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath(
            '//div[contains(@class,"videoPreview")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        item = SceneItem()
        jsondata = response.xpath('//script[@type="application/ld+json"]/text()').get()
        jsondata = jsondata.replace("\r\n", "")
        try:
            data = json.loads(jsondata.strip())
        except:
            print(f'JSON Data: {jsondata}')
        data = data[0]

        item['title'] = self.cleanup_title(data['name'])
        item['description'] = self.cleanup_description(data['description'].strip())

        item['date'] = self.parse_date(data['uploadDate'].strip()).isoformat()

        tags = data['keywords'].split(",")
        item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

        item['performers'] = list(
            map(lambda x: string.capwords(x['name'].strip()), data['actor']))

        item['url'] = response.url
        item['image'] = data['thumbnailUrl'].replace(" ", "%20")
        item['image_blob'] = None
        item['trailer'] = ''
        item['site'] = 'Bi Guys Fuck'
        item['parent'] = 'Bi Guys Fuck'
        item['network'] = 'Bi Guys Fuck'
        item['id'] = re.search(r'.*/(.*?)$', response.url).group(1)

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
