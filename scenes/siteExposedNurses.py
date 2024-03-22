import re
import html
import string
import slugify
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteExposedNursesSpider(BaseSceneScraper):
    name = 'ExposedNurses'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.exposednurses.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//th/h1/..')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('./h1/text()').get())
            item['description'] = ""
            item['date'] = ''
            item['image'] = ""
            item['image_blob'] = ""
            image = scene.xpath('.//img[@class="image1" and contains(@src, "1_3")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            performers = scene.xpath('.//b[contains(text(), "Nurse")]/following-sibling::text()[1]')
            item['performers'] = []
            if performers:
                performers = performers.getall()
                for performer in performers:
                    performer = html.unescape(performer.replace("&nbsp;", " ").replace("\xa0", " "))
                    if "(" in performer:
                        performer = re.search(r'(.*?) \(', performer).group(1)
                        item['performers'].append(performer.strip())
            tags = scene.xpath('.//b[contains(text(), "Tags")]/following-sibling::text()[1]')
            item['tags'] = []
            if tags:
                tags = tags.get()
                tags = tags.split(",")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            for tag in item['tags']:
                if "..." in tag:
                    item['tags'].remove(tag)
            item['trailer'] = ''
            item['id'] = slugify.slugify(item['title'].lower())
            item['network'] = "Apollo Cash"
            item['parent'] = "Exposed Nurses"
            item['site'] = "Exposed Nurses"
            item['url'] = f"https://www.exposednurses.com/{item['id']}"
            yield self.check_item(item, self.days)
