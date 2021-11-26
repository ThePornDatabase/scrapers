import re
from datetime import date, timedelta
import scrapy

from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper


class Site5DollahSpider(BaseSceneScraper):
    name = '5Dollah'
    network = '5Dollah'
    parent = '5Dollah'

    start_urls = [
        'https://www.5dollah.com/',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//div[@class="info"]/p/text()',
        'date': '//div[@class="info"]/text()[contains(.,"Date")]/following-sibling::span[1]/text()',
        'image': '//video/@poster',
        'performers': '//h1/following-sibling::a[contains(@href,"pornstars")]/strong/text()',
        'tags': '//text()[contains(.,"Tags")]/following-sibling::span/a/text()',
        'external_id': r'.*/(.*).html',
        'trailer': '//video/source/@src',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="col-item"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_site(self, response):
        return "5Dollah"

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if not item['image']:
            item['image'] = None

        item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)
            if item['tags'] and item['performers']:
                for performer in item['performers']:
                    if performer in item['tags']:
                        item['tags'].remove(performer)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        else:
            item['parent'] = self.get_parent(response)

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
