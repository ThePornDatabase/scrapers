from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from slugify import slugify


class NetworkPureEthnicSpider(BaseSceneScraper):
    name = 'PureEthnic'
    network = 'PureEthnic'

    start_urls = [
        'https://www.pureethnic.com',
    ]

    selector_map = {
        'title': './/comment()[contains(., "Title")]/following-sibling::a[1]/text()',
        'description': './/comment()[contains(., "Title")]/following-sibling::a[1]/@title',
        'date': './/div[contains(@class, "update_date")]/text()',
        'performers': './/span[@class="update_models"]/a/text()',
        'external_id': r'',
        'pagination': '/tour/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            item = SceneItem()
            item['id'] = scene.xpath('./@data-setid').get()
            item['title'] = super().get_title(scene)
            item['description'] = super().get_description(scene)
            image = scene.xpath('./a[1]/img/@src0_3x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['date'] = super().get_date(scene)
            item['network'] = 'Pure Ethnic'
            item['site'] = scene.xpath('.//a[@class="update_details_title"]/text()').get()
            item['site'] = item['site'].replace(".com", "")
            item['parent'] = 'Pure Ethnic'
            item['trailer'] = ''
            item['tags'] = []
            item['performers'] = super().get_performers(scene)
            item['url'] = 'https://www.pureethnic.com/tour/movies/' + slugify(item['title'].lower())
            yield self.check_item(item, self.days)
