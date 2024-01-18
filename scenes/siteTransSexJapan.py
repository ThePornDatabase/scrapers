import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTransSexJapanSpider(BaseSceneScraper):
    name = 'TransSexJapan'
    network = 'TransSexJapan'
    parent = 'TransSexJapan'
    site = 'TransSexJapan'

    start_urls = [
        'https://www.transexjapan.com',
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
        'pagination': '/models?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        models = response.xpath('//a[contains(@href, "/model/")]/@href').getall()
        for model in models:
            model_link = self.format_link(response, model)
            yield scrapy.Request(model_link, callback=self.get_model_scenes, meta=meta)

    def get_model_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "content-video")]')
        for scene in scenes:
            item = SceneItem()
            image = scene.xpath('./../@style').get()
            item['image'] = re.search(r'\((http.*)\)', image).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = re.search(r'tour/(.*?)/', item['image']).group(1)
            item['title'] = self.cleanup_title(scene.xpath('./div[contains(@class, "title")]/strong/text()').get())
            item['date'] = self.parse_date(scene.xpath('./div[contains(@class, "date")]/strong/text()').get(), date_formats=['%d %B. %Y']).strftime('%Y-%m-%d')
            item['performers'] = [self.cleanup_title(scene.xpath('//div[@class="model-name"]/text()').get())]
            duration = scene.xpath('./div[contains(@class, "title")]/strong/following-sibling::span/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d+)', duration).group(1)
                item['duration'] = str(int(duration) * 60)
            item['site'] = "TransSexJapan"
            item['network'] = "TransSexJapan"
            item['parent'] = "TransSexJapan"
            item['type'] = "Scene"
            item['tags'] = ['Trans', 'Asian']
            item['description'] = ''
            item['trailer'] = ''
            item['url'] = f"https://www.transexjapan.com/scene/{item['id']}"
            yield self.check_item(item, self.days)
