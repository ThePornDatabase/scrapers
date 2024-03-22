import re
import html
import string
import slugify
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteGapeMyPussySpider(BaseSceneScraper):
    name = 'GapeMyPussy'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.gapemypussy.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//table[@width="400"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//td[@height="36"]/text()').get())
            item['description'] = ""
            item['date'] = ''
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('.//img[contains(@src, "1_1")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performers = scene.xpath('.//span[contains(text(), "Model")]/b[1]/preceding-sibling::text()')
            item['performers'] = []
            if performers:
                performers = performers.getall()
                for performer in performers:
                    performer = html.unescape(performer.replace("&nbsp;", " ").replace("\xa0", " "))
                    if "(" in performer:
                        performer = re.search(r'(.*?) \(', performer).group(1)
                    if ":" in performer:
                        performer = re.search(r': (.*)', performer).group(1)
                    item['performers'].append(performer.strip())
            item['tags'] = ['Gaping']
            item['trailer'] = ''
            item['id'] = slugify.slugify(item['title'].lower())
            item['network'] = "Apollo Cash"
            item['parent'] = "Gape My Pussy"
            item['site'] = "Gape My Pussy"
            item['url'] = f"https://www.gapemypussy.com/{item['id']}"
            yield self.check_item(item, self.days)
