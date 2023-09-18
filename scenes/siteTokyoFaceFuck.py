import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTokyoFaceFuckSpider(BaseSceneScraper):
    name = 'TokyoFaceFuck'
    network = 'Tokyo Face Fuck'
    parent = 'Tokyo Face Fuck'
    site = 'Tokyo Face Fuck'

    start_urls = [
        'https://www.tokyofacefuck.com',
    ]

    selector_map = {
        'external_id': r'.*/(.*?)/',
        'pagination': '/en/?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "girl box")]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//div[@class="info"]/h1/text()')
            if title:
                title = self.cleanup_title(title.get())
                item['title'] = title

                if "," in title:
                    item['performers'] = title.split(",")
                else:
                    item['performers'] = [item['title']]
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
            else:
                item['title'] = ""
                item['performers'] = []

            item['date'] = ""
            description = scene.xpath('.//div[@class="info"]/div/p/text()')
            if description:
                item['description'] = " ".join(description.getall()).strip()
            else:
                item['description'] = ""

            image = scene.xpath('./div[contains(@class, "player")]/@style')
            if image:
                image = image.get()
                image = re.search(r'\((http.*?\.[a-zA-Z]{3})\)', image).group(1)
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)/', item['image']).group(1)
            else:
                item['image'] = ""
                item['image_blob'] = ""
                item['id'] = ""

            item['tags'] = ['Asian', 'Face Fuck', 'Blowjob']
            trailer = scene.xpath('./div/video/source/@src')
            if trailer:
                item['trailer'] = self.format_link(response, trailer.get())
            else:
                item['trailer'] = ""

            item['url'] = response.url
            item['site'] = 'Tokyo Face Fuck'
            item['parent'] = 'Tokyo Face Fuck'
            item['network'] = 'Tokyo Face Fuck'

            yield self.check_item(item, self.days)
