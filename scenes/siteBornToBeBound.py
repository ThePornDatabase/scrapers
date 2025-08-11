import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBornToBeBoundSpider(BaseSceneScraper):
    name = 'BornToBeBound'
    network = 'BornToBeBound'
    parent = 'BornToBeBound'
    site = 'BornToBeBound'

    start_urls = [
        'https://borntobebound.com',
    ]

    selector_map = {
        'title': '//h2/a/text()',
        'description': '//div[@class="art-PostContent"]/div[contains(@id, "gallery")]/following-sibling::div[1]/p[not(descendant::a)]//text()',
        'date': '//h2/following-sibling::div[contains(@class, "art-metadata-icons")]/text()[contains(., ",")]',
        'image': '//div[@class="art-PostContent"]/div[contains(@id, "gallery")]/dl[1]/dt//img/@src',
        'performers': '',
        'tags': '//a[@rel="tag"]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'p=(\d+)',
        'pagination': '/updates/?paged=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath('//h2/a/text()')
        if title:
            return super().get_title(response)
        return ""

    def parse_scene(self, response):
        item = self.init_scene()

        item['title'] = self.get_title(response)
        if item['title']:
            item['description'] = self.get_description(response)
            item['site'] = self.get_site(response)
            item['date'] = self.get_date(response)

            if self.check_item(item, self.days):
                item['image'] = self.get_image(response)
                if 'image' not in item or not item['image']:
                    item['image'] = None

                item['image_blob'] = self.get_image_blob(response)
                if ('image_blob' not in item or not item['image_blob']) and item['image']:
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if 'image_blob' not in item:
                    item['image_blob'] = None
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['performers'] = self.get_performers(response)
            item['tags'] = self.get_tags(response)
            item['id'] = self.get_id(response)
            item['trailer'] = self.get_trailer(response)
            item['url'] = self.get_url(response)
            item['network'] = self.get_network(response)
            item['parent'] = self.get_parent(response)
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)

    def get_tags(self, response):
        orig_tags = response.xpath('//a[@rel="tag"]/text()').getall()
        tags = []
        for tag in orig_tags:
            has_uppercase = bool(re.search(r'[A-Z]', tag))
            if not has_uppercase:
                tags.append(string.capwords(tag))
        tags.append("Bondage")
        return tags

    def get_performers(self, response):
        orig_tags = response.xpath('//a[@rel="tag"]/text()').getall()
        performers = []
        for tag in orig_tags:
            has_uppercase = bool(re.search(r'[A-Z]', tag))
            if has_uppercase:
                performers.append(string.capwords(tag))
        return performers
