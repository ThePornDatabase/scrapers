import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePlayboyTVSpider(BaseSceneScraper):
    name = 'PlayboyTV'
    site = 'Playboy TV'
    parent = 'Playboy TV'
    network = 'Playboy'

    start_urls = [
        'https://www.playboytv.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/episodes?page=%s&selected=episodes',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//li[@class="item"]')
        for scene in scenes:
            item = self.init_scene()

            show = scene.xpath('.//h3/text()').get()
            episode = scene.xpath('.//p[@class="subtitle"]/text()').get()
            item['title'] = f"{show} - {episode}"

            item['image'] = scene.xpath('.//img/@data-src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = re.search(r'.*/(\d+)/', item['image']).group(1)
            item['site'] = 'Playboy TV'
            item['parent'] = 'Playboy TV'
            item['network'] = 'Playboy'

            item['url'] = self.format_link(response, scene.xpath('.//a[@class="cardLink"]/@href').get())

            yield item
