import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCumEatingCuckoldsSpider(BaseSceneScraper):
    name = 'CumEatingCuckolds'
    site = 'Cum Eating Cuckolds'
    parent = 'Cum Eating Cuckolds'
    network = 'Cum Eating Cuckolds'

    start_urls = [
        'https://www.cumeatingcuckolds.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="preview-meta"]//p[@class="blurb"]/text()',
        'date': '//script[contains(@type, "ld+json") and contains(text(), "uploadDate")]/text()',
        're_date': r'"uploadDate":"([^"]+)"',
        'image': '//div[@class="update-preview"]/div[1]/img/@data-alt',
        'performers': '//div[@class="preview-meta"]//a[contains(@href, "models")]/text()',
        'tags': '',
        'external_id': r'.*/(\d+)',
        'pagination': '/tour/updates?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="tile update-card"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta, dont_filter=True)

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)

        item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None
            item['image_blob'] = None
        else:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        if item['image']:
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

        item['tags'] = self.get_tags(response)

        item['id'] = self.get_id(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['performers'] = self.get_performers(response)

        performers = response.xpath('//div[@class="preview-meta"]//a[contains(@href, "models")]/@href').getall()
        for performer in performers:
            meta['item'] = item.copy()
            performer = self.format_link(response, performer)
            yield scrapy.Request(performer, callback=self.parse_model, meta=meta, dont_filter=True)

    def parse_model(self, response):
        meta = response.meta
        performer = response.xpath('//a[contains(@href, "/models") and contains(text(), "Read Full")]/@href')
        if performer:
            performer = self.format_link(response, performer.get())
            yield scrapy.Request(performer, callback=self.parse_model_full, meta=meta, dont_filter=True)
        else:
            yield meta['item']

    def parse_model_full(self, response):
        meta = response.meta
        item = meta['item']
        perf_name = response.xpath('//div[@class="cec-model-hero"]//h1/text()').get()
        perf_name = string.capwords(perf_name)
        perf_image = response.xpath('//meta[@property="og:image"]/@content').get()
        perf_image_blob = self.get_image_blob_from_link(perf_image)
        perf_bio = response.xpath('//section[@class="cec-model-body"]//text()[not(contains(., "/join")) and not(contains(., "membership"))]').getall()
        if perf_bio:
            perf_bio = " ".join(perf_bio)

        item['performers_data'] = []
        perf = {}
        perf['name'] = perf_name
        perf['url'] = response.url
        perf['bio'] = perf_bio
        perf['site'] = 'Cum Eating Cuckolds'
        perf['network'] = 'Cum Eating Cuckolds'
        perf['image'] = perf_image
        perf['image_blob'] = perf_image_blob
        perf['extra'] = {'gender': "Female"}
        item['performers_data'].append(perf)

        scenes = response.xpath('//article[@class="cec-scene-card"]')
        for scene in scenes:
            scene_url = scene.xpath('./a[1]/@href').get()
            scene_id = re.search(r'.*/(\d+)', scene_url).group(1)
            if scene_id == item['id']:
                if not item['date']:
                    scene_date = scene.xpath('.//time/@datetime').get()
                    if scene_date:
                        scene_date = re.search(r'(\d{4}-\d{2}-\d{2})', scene_date)
                        if scene_date:
                            item['date'] = scene_date.group(1)
        yield item
