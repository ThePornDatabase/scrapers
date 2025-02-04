import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSecurityCamsFuckSpider(BaseSceneScraper):
    name = 'SecurityCamsFuck'

    start_urls = [
        'https://securitycamsfuck.com',
    ]

    selector_map = {
        'pagination': '/%s/',
        'external_id': r'',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-list-block"]//li/a')
        for scene in scenes:
            item = self.init_scene()
            item['performers'] = []
            item['tags'] = []
            item['trailer'] = ''
            item['image'] = ''
            item['description'] = ''
            item['network'] = "Security Cams Fuck"
            item['parent'] = "Security Cams Fuck"
            item['site'] = "Security Cams Fuck"

            title = scene.xpath('.//span[@class="description"]/span[@class="title"]/text()').get()
            if title:
                item['title'] = self.cleanup_title(title)

            duration = scene.xpath('.//i[@class="ico time"]/following-sibling::text()')
            if duration:
                item['duration'] = self.duration_to_seconds(duration.get())

            description = scene.xpath('.//div[@class="item-meta"]/div/text()').getall()
            if description:
                description = " ".join(description)
                description = description.replace("  ", " ")
                item['description'] = self.cleanup_description(description)

            item['date'] = ""

            image = scene.xpath('.//img[@class="thumb"]/@src').get()

            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['id'] = re.search(r'shots/.*?/(\d+)/', item['image']).group(1)
            item['url'] = f"https://securitycamsfuck.com/videos/{item['id']}/"

            yield item
