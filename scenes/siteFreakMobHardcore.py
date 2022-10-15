import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFreakMobHardcoreSpider(BaseSceneScraper):
    name = 'FreakMobHardcore'
    network = 'Freak Mob Media'
    parent = 'Freak Mob Media'
    site = 'Freak Mob Hardcore'

    start_urls = [
        'https://www.freakmobhardcore.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/models/models_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        models = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for model in models:
            yield scrapy.Request(url=self.format_link(response, model), callback=self.parse_model, meta=meta)

    def parse_model(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//span[@class="update_title"]/text()').get())
            description = scene.xpath('.//span[@class="latest_update_description"]/text()')
            if description:
                item['description'] = self.cleanup_text(description.get())
            else:
                item['description'] = ''
            item['performers'] = scene.xpath('.//span[@class="tour_update_models"]/a/text()').getall()
            item['date'] = self.parse_date('today').isoformat()
            item['tags'] = []
            trailer = scene.xpath('.//div[@class="update_image"]/a[1]/@onclick')
            if trailer:
                trailer = trailer.get()
                if ".mp4" in trailer:
                    trailer = self.format_link(response, re.search(r'\'(/.*\.mp4)', trailer).group(1)).replace(" ", "%20")
            if not trailer:
                trailer = None
            item['trailer'] = trailer
            item['image'] = self.format_link(response, scene.xpath('.//div[@class="update_image"]/a/img/@src0_2x').get()).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['site'] = "Freak Mob Hardcore"
            item['parent'] = "Freak Mob Media"
            item['network'] = "Freak Mob Media"
            item['url'] = response.url
            item['id'] = re.search(r'content/(.*?)/', item['image']).group(1)

            yield item
