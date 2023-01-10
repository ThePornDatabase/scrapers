import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteStockyDudesSpider(BaseSceneScraper):
    name = 'StockyDudes'

    start_urls = [
        'https://www.stockydudes.com',
    ]

    selector_map = {
        'title': './/div[@class="sceneTitle"]/text()',
        'description': './/div[@class="sceneDescription"]/text()',
        'date': '',
        'image': './/div[@class="bgScene"]/img/@src',
        'performers': './/span[@class="perfName"]/text()',
        'tags': './/span[@class="sceneTagsLnk"]/a/text()',
        'duration': '',
        'trailer': '///script[contains(text(), "jwplayer")]/text()',
        're_trailer': r'(http.*?\.mp4)',
        'external_id': r'',
        'pagination': '/scenes?Page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="eachScene"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.get_title(scene)
            item['date'] = self.get_date(scene)
            item['description'] = self.get_description(scene)
            item['image'] = self.get_image(scene, response.url)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)
            if "Gay" not in item['tags']:
                item['tags'].append("Homosexual")
            item['trailer'] = self.get_trailer(scene, response.url)
            item['type'] = 'Scene'
            item['duration'] = None
            item['url'] = response.url
            item['id'] = re.search(r'(\d+)', scene.xpath('./@id').get()).group(1)
            item['site'] = "Stocky Dudes"
            item['parent'] = "Stocky Dudes"
            item['network'] = "Stocky Dudes"
            yield item
