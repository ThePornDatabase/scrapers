import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteClaudiaMarieSpider(BaseSceneScraper):
    name = 'ClaudiaMarie'
    network = 'Claudia Marie'
    parent = 'Claudia Marie'

    start_urls = [
        'https://claudiamarie.com'
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
        'pagination': '/tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//h2/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)
            else:
                item['title'] = ''

            description = scene.xpath('.//span[contains(@class,"description")]/text()').get()
            if description:
                item['description'] = self.cleanup_description(description)
            else:
                item['description'] = ''

            performers = scene.xpath('.//span[contains(@class,"models")]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('.//span[contains(@class,"tags")]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            else:
                item['tags'] = []

            date = scene.xpath('.//span[contains(@class,"update_date")]/text()').get()
            if date:
                item['date'] = self.parse_date(date, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = []

            image = scene.xpath('.//div[contains(@class,"update_image")]/a[1]/img/@src').get()
            if image:
                item['image'] = "https://claudiamarie.com/tour/" + image.strip()
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('.//div[contains(@class,"update_image")]/a[1]/@onclick').get()
            if trailer:
                trailer = re.search(r'\(\'(.*)\'\)', trailer).group(1)
                if trailer:
                    item['trailer'] = "https://claudiamarie.com" + trailer.strip()
            else:
                item['trailer'] = []

            item['site'] = "Claudia Marie"
            item['parent'] = "Claudia Marie"
            item['network'] = "Claudia Marie"

            extern_id = item['title'].replace(" ", "-").replace("_", "-").strip().lower()
            extern_id = re.sub('[^a-zA-Z0-9-]', '', extern_id)
            if extern_id:
                item['id'] = extern_id.strip()

            item['url'] = "https://claudiamarie.com/tour/updates/" + item['id'] + ".html"

            yield item
