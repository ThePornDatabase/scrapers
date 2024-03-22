import re
import string
import slugify
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSheFuckedHerSpider(BaseSceneScraper):
    name = 'SheFuckedHer'
    network = 'Apollo Cash'

    start_urls = [
        'https://shefuckedher.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//table[@bgcolor="black"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//td/h1/text()').get())
            item['description'] = ""
            description = scene.xpath('.//font[contains(@face, "SunSans-Regular") and @size="4"]/text()')
            if description:
                item['description'] = " ".join(list(map(lambda x: x.strip(), description.getall()))).strip().replace("\n", "").replace("\t", "").replace("\r", "")
            item['date'] = ''
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('.//th[@align="left"]/a/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performers = scene.xpath('.//font[contains(@face, "SunSans-Regular") and @size="6"]/b/text()')
            item['performers'] = []
            if performers:
                performers = performers.getall()
                for performer in performers:
                    if "(" in performer:
                        item['performers'].append(re.search(r'(.*?) \(', performer).group(1))
            tags = scene.xpath('.//b[contains(text(), "Tags")]/following-sibling::text()[1]')
            item['tags'] = []
            if tags:
                tags = tags.get()
                tags = tags.split(",")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            item['trailer'] = ''
            item['id'] = slugify.slugify(item['title'].lower())
            item['network'] = "Apollo Cash"
            item['parent'] = "She Fucked Her"
            item['site'] = "She Fucked Her"
            item['url'] = f"https://shefuckedher.com/{item['id']}"
            yield self.check_item(item, self.days)
