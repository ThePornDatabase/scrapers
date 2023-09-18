import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBrokeModelSpider(BaseSceneScraper):
    name = 'BrokeModel'
    network = 'Broke Model'
    parent = 'Broke Model'
    site = 'Broke Model'

    start_urls = [
        'https://free.brokemodel.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour3/models/models_%s_d.html?g=f',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        models = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for model in models:
            yield scrapy.Request(url=self.format_link(response, model), callback=self.get_model_scenes, meta=meta)

    def get_model_scenes(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//span[@class="update_title"]/text()').get())
            item['description'] = ""
            description = scene.xpath('.//span[contains(@class, "description")]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())
            item['date'] = ''
            scenedate = scene.xpath('.//span[contains(@class, "update_date")]/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%m/%d/%Y']).isoformat()
            item['performers'] = scene.xpath('.//span[contains(@class, "update_models")]/a/text()').getall()
            item['tags'] = scene.xpath('.//span[contains(@class, "update_tags")]/a/text()').getall()
            item['image'] = "https://free.brokemodel.com/tour3/" + scene.xpath('.//img[contains(@class, "large_update_thumb")]/@src|.//div[@class="update_image"]//a/comment()[contains(., "First")]/following-sibling::img/@src0_2x').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ""
            trailer = scene.xpath('.//a[contains(@onclick, "tload")]/@onclick')
            if trailer:
                trailer = re.search(r'\'(/trailer.*?)\'', trailer.get())
                if trailer:
                    item['trailer'] = "https://free.brokemodel.com" + trailer.group(1)
            item['type'] = "Scene"
            item['site'] = "Broke Model"
            item['parent'] = "Broke Model"
            item['network'] = "Broke Model"
            item['id'] = re.search(r'content/(.*?)/', item['image']).group(1)
            item['url'] = response.url

            yield self.check_item(item, self.days)
