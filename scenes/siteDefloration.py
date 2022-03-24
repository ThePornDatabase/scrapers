import re
from datetime import date, timedelta
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDeflorationSpider(BaseSceneScraper):
    name = 'Defloration'
    network = 'Defloration'
    parent = 'Defloration'
    site = 'Defloration'

    start_urls = [
        'https://blog.defloration.com',
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//div[@class="entry-content"]/article//text()',
        'date': '//div[@class="entry-meta-top"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="entry-content"]/article//img/@src',
        'image_blob': True,
        'performers': '//h1[@class="entry-title"]/text()',
        'tags': '',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "post-")]//a[contains(text(), "Read More")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = ['Hymen', 'Defloration', 'Virgin']
        return tags

    def get_performers(self, response):
        title = super().get_performers(response)[0]
        performer = ''
        if title:
            if re.search(r'(\w+ \w+)\.', title):
                performer = re.search(r'(\w+ \w+)\.', title).group(1)
            else:
                if len(re.findall(r'\w+', title)) == 2:
                    performer = title.strip()
        return [string.capwords(performer)]

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

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
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

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if 'image_blob' not in item or not item['image_blob']:
            item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

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
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        if self.days > 27375:
            filter_date = '0000-00-00'
        else:
            days = self.days
            filter_date = date.today() - timedelta(days)
            filter_date = filter_date.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filter_date:
                item['filtered'] = 'Scene filtered due to date restraint'
            print(item)
        else:
            if filter_date and item['image']:
                if item['date'] > filter_date:
                    yield item
            else:
                if item['image']:
                    yield item
