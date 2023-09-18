import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePissListSpider(BaseSceneScraper):
    name = 'PissList'

    start_urls = [
        'http://www.pisslist.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/public/most-recent/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item"]')
        for scene in scenes:
            item = SceneItem()

            title1 = self.cleanup_text(scene.xpath('.//a[@class="vidLinkName"]/text()').get())
            title2 = self.cleanup_text(scene.xpath('.//span[@class="underName"]/text()').get())
            item['title'] = title1 + " " + title2
            scenedate = scene.xpath('.//div[contains(@class, "vidData")]/span[contains(text(), "-")]/text()').get()
            scenedate = re.search(r'(\d{2}-\d{2}-\d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%d-%m-%Y']).isoformat()
            item['description'] = scene.xpath('.//div[@class="descriptionBox"]/text()').get()
            performers = scene.xpath('.//a[@class="vidLinkName"]/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            item['trailer'] = ''
            tags = scene.xpath('.//div[@class="subListCats"]/a/text()').getall()
            item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            image = scene.xpath('./a/img[contains(@src, "scene")]/@src').get()
            item['image'] = self.format_link(response, image).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            duration = scene.xpath('.//div[contains(@class, "vidData")]/span[contains(text(), "mins")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d{1,2}:\d{1,2})', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)

            item['url'] = self.format_link(response, scene.xpath('./div[@class="meta"]/div[contains(@class, "left")]/a/@href').get())
            item['id'] = scene.xpath('./@data-scene-id').get()

            item['site'] = 'Piss List'
            item['parent'] = 'Piss List'
            item['network'] = 'Piss List'

            yield self.check_item(item, self.days)
