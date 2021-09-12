import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VrAllureSpider(BaseSceneScraper):
    name = 'VrAllure'
    network = "Radical Entertainment"
    parent = "VrAllure"

    start_urls = [
        'https://vrallure.com/'
    ]

    selector_map = {
        'title': '//deo-video/@title',
        'description': '//p[@class="desc"]/span/text()',
        'date': '//p[@class="publish-date"]/img/following-sibling::text()',
        'image': '//deo-video/@cover-image',
        'performers': '//p[@class="model-name"]/a/text()',
        'tags': '//p[@class="tag-container"]/a/text()',
        'trailer': '',
        'external_id': '\\/scenes\\/(vr.*?)_',
        'pagination': '/?page=%s'
    }

    def get_scenes(self, response):

        scenes = response.xpath(
            '//h4[@class="latest-scene-title"]/a/@href').getall()
        for scene in scenes:
            if '?nats' in scene:
                scene = re.search('(.*)\\?nats', scene).group(1)

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
