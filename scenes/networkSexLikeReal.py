import re
from datetime import date, timedelta
import scrapy
from extruct.jsonld import JsonLdExtractor

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SexLikeRealSpider(BaseSceneScraper):
    name = 'SexLikeReal'
    network = 'SexLikeReal'

    start_urls = [
        'https://www.sexlikereal.com'
    ]

    selector_map = {
        'title': "//title/text()",
        'description': "//div[@class='u-mb--four u-lh--opt u-fs--fo u-fw--medium u-lw']/text()",
        'date': "//time[1]/@datetime",
        'performers': "//meta[@property='video:actor']/@content",
        'tags': "//meta[@property='video:tag']/@content",
        'external_id': '(?:scenes|shemale|gay)\\/(.+)',
        'image': '//meta[@name="twitter:image1"]/@content or //meta[@name="twitter:image2"]/@content or //meta[@name="twitter:image3"]/@content or //meta[@name="twitter:image"]/@content',
        'trailer': '',
        'pagination': '/scenes?type=new&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'c-grid--scenes')]//article[contains(@class, 'c-grid-item--scene')]//a[1]/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        jslde = JsonLdExtractor()
        json = jslde.extract(response.text)
        data = {}
        for obj in json:
            if obj['@type'] == 'VideoObject':
                data = obj
                break

        item = SceneItem()
        item['title'] = self.cleanup_title(data['name'])
        item['description'] = self.cleanup_description(data['description'])
        item['image'] = data['thumbnail']
        item['image_blob'] = None
        item['id'] = self.get_id(response)
        item['trailer'] = data['contentUrl']
        item['url'] = response.url
        item['date'] = self.parse_date(data['datePublished']).isoformat()
        item['site'] = data['author']['name']
        item['network'] = self.network
        item['parent'] = item['site']

        item['performers'] = []
        for model in data['actor']:
            item['performers'].append(model['name'])

        item['tags'] = self.get_tags(response)
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
