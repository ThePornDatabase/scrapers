import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMuscleBoyWrestlingSpider(BaseSceneScraper):
    name = 'MuscleBoyWrestling'

    start_urls = [
        'https://muscleboywrestling.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/catalog?alias=catalogs&page=%s&per-page=10',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        catalogs = response.xpath('//div[contains(@class, "catalog")]/div[@class="row"]/div[1]/a[1]/@href').getall()
        for catalog in catalogs:
            yield scrapy.Request(url=self.format_link(response, catalog), callback=self.parse_catalog, meta=meta)

    def parse_catalog(self, response):
        cat_title = response.xpath('//h1/text()').get()
        cat_title = string.capwords(cat_title.rstrip(string.punctuation))

        scenes = response.xpath('//div[contains(@class, "video card")]')
        for scene in scenes:
            item = self.init_scene()
            item['date'] = self.parse_date(response.xpath('//h1/following-sibling::p[1]/text()').get()).strftime('%Y-%m-%d')
            scene_title = string.capwords(scene.xpath('.//h3/a/text()').get()).replace("Vs", "vs")
            item['title'] = cat_title + ": " + scene_title
            if " vs " in scene_title.lower():
                item['performers'] = scene_title.split(" vs ")
                item['performers_data'] = self.get_performers_data(item['performers'])
            item['tags'] = ['Gay', 'Wrestling', 'Sports']

            item['description'] = self.cleanup_description(scene.xpath('.//div[contains(@class, "card-text")]/p/text()').get())

            image = scene.xpath('.//img/@src')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['url'] = self.format_link(response, scene.xpath('.//h3/a/@href').get())
            item['id'] = re.search(r'video/(\w+-\w+)-.*', item['url']).group(1)
            item['site'] = 'Muscle Boy Wrestling'
            item['parent'] = 'Muscle Boy Wrestling'
            item['network'] = 'Muscle Boy Wrestling'

            yield self.check_item(item, self.days)

    def get_performers_data(self, performers):
        performers_data = []
        for performer in performers:
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "Muscle Boy Wrestling"
            performer_extra['site'] = "Muscle Boy Wrestling"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
