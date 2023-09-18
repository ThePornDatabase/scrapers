import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDreamstashSpider(BaseSceneScraper):
    name = 'Dreamstash'
    network = 'Dreamstash'
    parent = 'Dreamstash'
    site = 'Dreamstash'

    start_urls = [
        'https://dreamstash.com',
    ]

    selector_map = {
        'title': './article/div[1]/a[1]/@title',
        'description': '',
        'date': './/time[@class="entry-date"]/@datetime',
        'image': './article/div[1]/a[1]/div[1]/img[1]/@data-src',
        'performers': './/span[@class="entry-author"]//strong/text()',
        'tags': '',
        'duration': './/span[contains(@class, "video-duration")]/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/movies/page/%s/#',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@id="primary"]//li[contains(@class,"ax-collection-item")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = super().get_title(scene)
            item['url'] = self.format_link(response, scene.xpath('./article/div[1]/a[1]/@href').get())
            item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
            item['description'] = ''
            scenedate = super().get_date(scene)
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate).group(1)
            item['image'] = self.format_link(response, super().get_image(scene, response.url))
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = super().get_performers(scene)
            item['tags'] = []
            item['duration'] = super().get_duration(scene)
            item['trailer'] = ''
            item['site'] = 'Dreamstash'
            item['parent'] = 'Dreamstash'
            item['network'] = 'Dreamstash'
            yield self.check_item(item, self.days)
