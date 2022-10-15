import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFemjoySpider(BaseSceneScraper):
    name = 'Femjoy'
    network = 'Femjoy'
    parent = 'Femjoy'
    site = 'Femjoy'

    start_urls = [
        'https://www.femjoy.com',
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
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "results_item")]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('./div/h1/a[1]/text()').get())
            item['date'] = self.parse_date(scene.xpath('./div//span[@class="posted_on"]/text()').get(), date_formats=['%b %d, %Y']).isoformat()
            item['duration'] = self.duration_to_seconds(scene.xpath('./div//span[@class="posted_on"]/following-sibling::span/text()').get())
            item['director'] = scene.xpath('.//h2/a[contains(@href, "/director/")]/text()').get()
            item['performers'] = scene.xpath('.//h2/a[contains(@href, "/models/")]/text()').getall()
            item['site'] = 'Femjoy'
            item['parent'] = 'Femjoy'
            item['network'] = 'Femjoy'
            item['type'] = 'Scene'
            item['image'] = scene.xpath('./div/div/a/img[contains(@class, "item_cover")]/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = re.search(r'\.com/(\d*?)/', item['image']).group(1)
            item['tags'] = []
            item['trailer'] = ''
            item['url'] = self.format_link(response, scene.xpath('./div/div/a/@href').get())
            meta['item'] = item
            yield scrapy.Request(item['url'], callback=self.get_description, headers=self.headers, cookies=self.cookies, meta=meta)

    def get_description(self, response):
        item = response.meta['item']
        description = response.xpath('//h2[@class="post_description"]/p')
        if description:
            item['description'] = description.get().strip()
        else:
            item['description'] = ''

        yield self.check_item(item, self.days)
