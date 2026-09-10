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
        # The model pages this used to walk are broken server-side: the CMS emits
        # "Uncaught Error: Undefined constant ZoneId" and renders no updates at all,
        # so a crawl fetched 96 model pages and produced nothing.  The scenes listing
        # at /tour3/categories/ carries them directly.
        'pagination': '/tour3/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for scene in response.xpath('//div[@class="updateItem"]'):
            item = SceneItem()

            title = scene.xpath('.//div[@class="updateDetails"]//h4/a/text()').get()
            if not title or not title.strip():
                continue
            item['title'] = self.cleanup_title(title)
            item['description'] = ""

            # the still doubles as the identifier: content/<set>/<n>.jpg
            image = scene.xpath('./a/img/@src0_4x').get() or scene.xpath('./a/img/@src').get()
            if not image:
                continue
            item['image'] = self.format_link(response, image)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            sceneid = re.search(r'content/([^/]+)/', image)
            if not sceneid:
                continue
            item['id'] = sceneid.group(1)
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get() or image)

            item['date'] = ''
            for text in scene.xpath('.//div[@class="updateDetails"]//span/text()').getall():
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', text)
                if scenedate:
                    scenedate = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y'])
                    if scenedate:
                        item['date'] = scenedate.isoformat()
                    break

            item['performers'] = [x.strip() for x in
                                  scene.xpath('.//span[contains(@class, "tour_update_models")]/a/text()').getall()
                                  if x and x.strip()]
            item['tags'] = []
            item['trailer'] = ""
            item['site'] = "Broke Model"
            item['parent'] = "Broke Model"
            item['network'] = "Broke Model"

            yield self.check_item(item, self.days)

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
