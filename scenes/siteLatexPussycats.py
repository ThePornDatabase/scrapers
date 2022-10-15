import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLatexPussycatsSpider(BaseSceneScraper):
    name = 'LatexPussycats'

    start_urls = [
        'https://www.latexpussycats.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/latex/movies.php?&p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoBlock"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//h4/a/text()').get())
            item['description'] = ''
            scenedate = scene.xpath('.//div[contains(@class, "date")]/text()')
            if scenedate:
                item['date'] = self.parse_date (scenedate.get(), date_formats=['%Y-%m-%d']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//div/a/img/@src')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'/(\d+)\.jpg', image).group(1)
            else:
                item['image'] = ''
                item['image_blob'] = ''
                item['id'] = ''
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['url'] = response.url
            item['site'] = 'Latex Pussycats'
            item['parent'] = 'Latex Pussycats'
            item['network'] = 'Latex Pussycats'

            yield self.check_item(item, self.days)
