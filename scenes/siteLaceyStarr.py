import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLaceyStarrSpider(BaseSceneScraper):
    name = 'LaceyStarr'

    start_urls = [
        'https://www.laceystarr.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/granny/updates.php?&p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="otherScene"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//h4//text()').get())
            item['description'] = ''
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                item['date'] = self.parse_date (scenedate.get(), date_formats=['%B %d, %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            image = scene.xpath('.//img/@src')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'/(\d+)\.jpg', image).group(1)
            else:
                item['image'] = ''
                item['image_blob'] = ''
                item['id'] = ''
            item['performers'] = scene.xpath('.//p[contains(text(), "Starring")]/a/text()').getall()
            if "Lacey Starr" not in item['performers']:
                item['performers'].append("Lacey Starr")
            item['tags'] = ['GILF', 'Older / Younger']
            item['trailer'] = ''
            item['url'] = response.url
            item['site'] = 'Lacey Starr'
            item['parent'] = 'Lacey Starr'
            item['network'] = 'Lacey Starr'

            yield self.check_item(item, self.days)
