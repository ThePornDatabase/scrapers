import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCoverMyFaceSpider(BaseSceneScraper):
    name = 'CoverMyFace'

    start_urls = [
        'https://www.covermyface.com'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/home.php?page=%s',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="boxVideo"]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene.xpath('./div[1]/table//tr[not(@class="txtTech")]/td[1]/text()').get())
            item['performers'] = [item['title']]

            duration = scene.xpath('./div[1]/table//tr[not(@class="txtTech")]/td[2]/text()')
            if duration:
                item['duration'] = self.duration_to_seconds(duration.get())

            description = scene.xpath('./div[contains(@style, "margin:")]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())

            image = scene.xpath('.//table[@class="imgBdrDark"]//td[@align="left"]/img/@src')
            if image:
                image = image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

                item['id'] = re.search(r'images/(.*?)/', image).group(1)

            item['type'] = "Scene"
            item['site'] = 'Cover My Face'
            item['parent'] = 'Cover My Face'
            item['network'] = 'Cover My Face'

            item['url'] = f"https://www.covermyface.com/video/{item['id']}"

            yield item
