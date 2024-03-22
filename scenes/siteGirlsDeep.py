import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class siteGirlsDeepSpider(BaseSceneScraper):
    name = 'GirlsDeep'
    site = 'Girls Deep'
    parent = 'Girls Deep'
    network = 'Girls Deep'

    start_urls = [
        'https://girlsdeep.com',
    ]

    selector_map = {
        'title': './/h3/a/text()',
        'description': './/div[contains(@class,"entry-summary")]/p[1]/text()',
        'date': './/time/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'performers': './/span[contains(text(), "MODEL:")]/following-sibling::a[1]/strong/text()',
        'tags': './/span[contains(@class,"entry-categories-inner")]/a/text()',
        'duration': './/span[contains(@class,"video-duration")]/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[contains(@class,"ax-collection-item-1of2")]/article[contains(@class, "post-format-video")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            image = scene.xpath('.//div[contains(@class,"entry-featured-media")]//img[contains(@data-src, "uploads")]/@data-src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['duration'] = self.get_duration(scene)
            item['type'] = 'Scene'
            item['url'] = self.format_link(response, scene.xpath('./div[1]/a[1]/@href').get())
            item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
            item['site'] = "Girls Deep"
            item['parent'] = "Girls Deep"
            item['network'] = "Girls Deep"
            item['tags'] = self.get_tags(scene)
            if 'ArianaBright' in item['tags']:
                item['tags'].remove('ArianaBright')
            item['performers'] = self.get_performers(scene)
            item['trailer'] = ''

            if "TRAILERS" not in item['tags']:
                yield self.check_item(item, self.days)
