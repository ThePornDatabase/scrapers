import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTransSexJapanSpider(BaseSceneScraper):
    name = 'TranSexJapan'
    network = 'TranSexJapan'
    parent = 'TranSexJapan'
    site = 'TranSexJapan'

    start_urls = [
        'https://www.transexjapan.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/models?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        models = response.xpath('//a[contains(@href, "/model/")]/@href').getall()
        for model in models:
            model_link = self.format_link(response, model)
            yield scrapy.Request(model_link, callback=self.get_model_scenes, meta=meta)

    def get_model_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "content-video")]')
        for scene in scenes:
            item = self.init_scene()
            image = scene.xpath('./../@style').get()
            item['image'] = re.search(r'\((http.*)\)', image).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = re.search(r'tour/(.*?)/', item['image']).group(1)
            item['title'] = self.cleanup_title(scene.xpath('./div[contains(@class, "title")]/strong/text()').get())
            scenedate = scene.xpath('./div[contains(@class, "date")]/strong/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%d %B. %Y']).strftime('%Y-%m-%d')
            item['performers'] = [self.cleanup_title(scene.xpath('//div[@class="model-name"]/text()').get())]
            duration = scene.xpath('./div[contains(@class, "title")]/strong/following-sibling::span/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d+)', duration).group(1)
                item['duration'] = str(int(duration) * 60)
            item['performers_data'] = self.get_performers_data(item['performers'])
            item['site'] = "TranSexJapan"
            item['network'] = "TranSexJapan"
            item['parent'] = "TranSexJapan"
            item['type'] = "Scene"
            item['tags'] = ['Trans', 'Asian']
            item['description'] = ''
            item['trailer'] = ''
            item['url'] = f"https://www.transexjapan.com/scene/{item['id']}"
            yield self.check_item(item, self.days)

    def get_performers_data(self, performers):
        performers_data = []
        for performer in performers:
            performer_data = {}
            performer_data['name'] = performer.strip()
            performer_data['site'] = "TranSexJapan"
            performer_data['extra'] = {}
            performer_data['extra']['gender'] = "Transgender Female"
            performers_data.append(performer_data)
        return performers_data