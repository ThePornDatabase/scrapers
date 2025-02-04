import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTrueAmateurModelsSpider(BaseSceneScraper):
    name = 'TrueAmateurModels'

    start_urls = [
        'https://trueamateurmodels.com',
    ]

    selector_map = {
        'title': './/span[@class="update_title"]/text()',
        'description': './/span[@class="latest_update_description"]/text()',
        'date': './/span[@class="availdate"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'performers': './/span[@class="tour_update_models"]/a/text()',
        'tags': './/span[@class="update_tags"]/a/text()',
        'external_id': r'',
        'pagination': '/previewtour/models/models_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.get_model_scenes, meta=meta)

    def get_model_scenes(self, response):
        scenes = response.xpath('//text()[contains(., "of video")]/../../../../..')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            item['tags'] = self.get_tags(scene)
            performers = self.get_performers(scene)
            item['performers'] = []
            item['performers_data'] = []
            for performer in performers:
                performer = performer.replace("Model", "").strip()
                performer_extra = {}
                performer_extra['name'] = performer
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = "Female"
                perf_image = response.xpath('//div[contains(@class,"model_picture")]/img/@src0_3x|//div[contains(@class,"model_picture")]/img/@src0_2x|//div[contains(@class,"model_picture")]/img/@src0_1x')
                if perf_image:
                    perf_image = perf_image.get()
                    performer_extra['image'] = "https://trueamateurmodels.com/" + perf_image
                    performer_extra['image_blob'] = self.get_image_blob_from_link(performer_extra['image'])
                item['performers_data'].append(performer_extra)
                item['performers'].append(performer)

            sceneimage = scene.xpath('.//div[@class="update_image"]/a/img/@src0_3x|.//div[@class="update_image"]/a/img/@src0_2x|.//div[@class="update_image"]/a/img/@src0_1x')
            if sceneimage:
                sceneimage = "https://trueamateurmodels.com/previewtour/" + sceneimage.get()
                item['image'] = sceneimage
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['id'] = re.search(r'content/(.*?)/', item['image']).group(1)
            item['url'] = "https://trueamateurmodels.com/previewtour/" + item['id']
            item['site'] = 'True Amateur Models'
            item['parent'] = 'True Amateur Models'
            item['network'] = 'True Amateur Models'
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
