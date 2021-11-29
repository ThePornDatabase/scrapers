import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLarasPlaygroundSpider(BaseSceneScraper):
    name = 'LarasPlayground'
    network = 'Laras Playground'
    max_pages = 35

    start_urls = [
        'https://www.larasplayground.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//p[contains(@class, "description")]/text()',
        'performers': '//span[contains(@class,"models")]/a/text()',
        'date': '//div[contains(@class, "date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-tags")]/a/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/index.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(r'//div[@class="serie"]')
        if response.meta['page'] < self.max_pages:
            for scene in scenes:
                item = SceneItem()
                title = scene.xpath(r'./div/div[@class="serie_tekst"]'
                                    '/strong/text()').get()
                if title:
                    item['title'] = self.cleanup_title(title)
                else:
                    item['title'] = ''

                description = scene.xpath(r'./div/div[@class="serie_tekst"]'
                                          '/strong/following-sibling::text()'
                                          ).get()
                if description:
                    item['description'] = self.cleanup_description(description)
                else:
                    item['description'] = ''

                item['performers'] = ['Lara Latex']
                item['tags'] = []
                item['date'] = self.parse_date('today').isoformat()

                image = scene.xpath(r'./div/div[@class="serie_pic01"]/img/@src')
                if image:
                    image = image.get()
                    item['image'] = image.strip()
                else:
                    item['image'] = None

                item['image_blob'] = None

                item['trailer'] = ''
                item['site'] = "Laras Playground"
                item['parent'] = "Laras Playground"
                item['network'] = "Laras Playground"

                extern_id = re.search(r'.*\/(\d+)\/.*?\.jpg', item['image'])
                if extern_id:
                    item['id'] = extern_id.group(1).strip()

                item['url'] = response.url

                yield item
