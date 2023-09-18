from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteWifeysWorldSpider(BaseSceneScraper):
    name = 'WifeysWorld'
    network = 'Wifeys World'
    parent = 'Wifeys World'
    site = 'Wifeys World'

    start_urls = [
        'https://wifeysworld.com',
    ]

    selector_map = {
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/v3/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "grid__item")]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = scene.xpath('./a//span[contains(@class, "title")]/text()').get()
            item['description'] = ""
            item['site'] = "Wifeys World"
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::span/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = None
            image = scene.xpath('./a/span/img/@src0_3x')
            if image:
                item['image'] = "https://wifeysworld.com/v3/tour/" + image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None
            item['performers'] = None
            item['tags'] = None
            item['markers'] = None
            item['id'] = scene.xpath('./@data-setid').get()
            item['trailer'] = None
            duration = scene.xpath('.//i[contains(@class, "clock")]/following-sibling::span/text()')
            if duration:
                item['duration'] = str(int(duration.get()) * 60)
            else:
                item['duration'] = None
            item['url'] = response.url
            item['network'] = "Wifeys World"
            item['parent'] = "Wifeys World"
            item['type'] = 'Scene'

            if item['date'] > '2023-03-08':
                yield self.check_item(item, self.days)
