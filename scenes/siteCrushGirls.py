import re
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False

class SiteCrushGirlsSpider(BaseSceneScraper):
    name = 'CrushGirls'

    start_urls = [
        'https://crushgirls.com'
    ]

    selector_map = {
        'type': 'Scene',
        'external_id': r'view/(\d+)/',
        'pagination': '/videos?page=%s',
    }

    cookies = []

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumbs"]')
        for scene in scenes:
            item = self.init_scene()

            item['url'] = self.format_link(response, scene.xpath('./div[1]/a[1]/@href').get())

            item['id'] = re.search(r'view/(\d+)/', item['url']).group(1)

            item['title'] = self.cleanup_title(scene.xpath('.//h4/text()').get())

            image = scene.xpath('.//img/@src').get()
            image = image.replace("-1x", "-full")
            item['image'] = self.format_link(response, image)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['description'] = self.cleanup_description(scene.xpath('.//p[@class="description"]/text()').get())

            duration = scene.xpath('.//p[contains(text(), "Video:")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)

            item['site'] = "CrushGirls"
            item['parent'] = "CrushGirls"
            item['network'] = "CrushGirls"
            item['type'] = "Scene"

            yield item
