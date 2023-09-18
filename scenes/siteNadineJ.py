import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNadineJSpider(BaseSceneScraper):
    name = 'NadineJ'
    network = 'Nadine J'
    parent = 'Nadine J'
    site = 'Nadine J'

    start_urls = [
        'https://nadine-j.de',
    ]

    selector_map = {
        'title': './/h2[contains(@class, "text-light")]/text()',
        'description': './/h2[contains(@class, "text-light")]/following-sibling::div//text()|.//p/span/text()',
        'date': './/div[@class="col-sm-6"]/div[1]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': './/img/@src',
        'performers': '',
        'tags': '',
        'duration': './/a[contains(text(), "min")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/models/videos/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="video-teaser"]')
        for scene in scenes:
            item = SceneItem()
            item['url'] = self.format_link(response, scene.xpath('.//a[contains(text(), "min")]/@href').get())
            item['id'] = re.search(r'.*/(\d+)$', item['url']).group(1)
            item['title'] = super().get_title(scene)
            item['date'] = super().get_date(scene)
            item['description'] = super().get_description(scene)
            item['image'] = self.format_link(response, super().get_image(scene, response.url))
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = ["Big Boobs"]
            item['duration'] = super().get_duration(scene)
            item['trailer'] = None
            item['performers'] = []
            performers = scene.xpath('.//h2[contains(@class, "text-dark")]/text()')
            if performers:
                performers = performers.get()
                if "&" in performers:
                    item['performers'] = performers.split("&")
                    item['performers'] = list(map(lambda x: x.strip(), item['performers']))
                else:
                    item['performers'] = [performers]
            item['site'] = "Nadine J"
            item['parent'] = "Nadine J"
            item['network'] = "Nadine J"

            yield self.check_item(item, self.days)
