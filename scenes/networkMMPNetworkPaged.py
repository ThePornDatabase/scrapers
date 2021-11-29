import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMMPNetworkSpider(BaseSceneScraper):
    name = 'MMPNetworkPaged'
    network = 'MMP Network'

    start_urls = [
        'https://myfirstpublic.com',
        'https://shootourself.com',
        'https://teenyplayground.com',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="wrapper" and ./div[@class="scenewrapper"]]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//h1/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = ''

            item['description'] = ''
            item['performers'] = []
            item['date'] = self.parse_date('today').isoformat()
            image = scene.xpath('./div/div[@class="snapshot"]/img/@src|./div/div//video/@poster').get()
            if image:
                item['image'] = self.format_link(response, image)
                item['id'] = re.search(r'\.com/(.*?)/.*', image).group(1).strip()
            else:
                item['image'] = ''
                item['id'] = ''

            tags = scene.xpath('.//div[@class="tags"]/a/text()')
            if tags:
                item['tags'] = list(map(lambda x: x.strip().title(), tags.getall()))
            else:
                item['tags'] = []

            if "myfirstpublic" in response.url:
                item['site'] = "My First Public"
                item['parent'] = "My First Public"
            if "shootourself" in response.url:
                item['site'] = "Shoot Ourself"
                item['parent'] = "Shoot Ourself"
            if "teenyplayground" in response.url:
                item['site'] = "Teeny Playground"
                item['parent'] = "Teeny Playground"

            item['network'] = 'MMP Network'

            item['image_blob'] = ''
            item['trailer'] = ''
            item['url'] = response.url

            if item['id'] and item['title']:
                yield item
