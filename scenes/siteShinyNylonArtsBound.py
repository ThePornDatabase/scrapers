import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteShinyNylonArtsBoundSpider(BaseSceneScraper):
    name = 'ShinyNylonArtsBound'
    network = 'Shiny Nylon Arts Bound'
    parent = 'Shiny Nylon Arts Bound'
    site = 'Shiny Nylon Arts Bound'
    start_urls = [
        'https://www.shinynylonartsbound.com',
    ]

    selector_map = {
        'title': './/h2/a/text()',
        'description': './/div[contains(@class, "custom_text")]/p/text()',
        'date': './/div[contains(@class, "init-video")]/@data-sources',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': './/div[contains(@class, "init-video")]/@data-attributes',
        're_image': r'(https://images.*?)\"',
        'tags': './/a[contains(@href, "/collections?category")]/text()',
        'duration': './/span[contains(text(), "minutes")]/text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': './/div[contains(@class, "init-video")]/@data-sources',
        're_trailer': r'src\":.*?\"(http.*?)\"',
        'external_id': r'',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="collection"]')
        for scene in scenes:
            item = self.init_scene()
            sceneid = scene.xpath('./@id').get()
            item['id'] = re.search(r'_(\d+)', sceneid).group(1)
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            if not item['date']:
                scenedate = scene.xpath('.//div[contains(@class, "init-video")]/@data-sources')
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'.*/(\d{8})', scenedate)
                    if scenedate:
                        scenedate = scenedate.group(1)
                        item['date'] = self.parse_date(scenedate, date_formats=['%Y%m%d'])
                        if item['date']:
                            item['date'] = item['date'].strftime('%Y-%m-%d')

            image = scene.xpath('.//div[contains(@class, "init-video")]/@data-attributes').get()
            if image:
                image = re.search(r'(https://images.*?)\"', image)
                if image:
                    item['image'] = image.group(1)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['tags'] = self.get_tags(scene)
            item['duration'] = self.get_duration(scene)
            item['trailer'] = self.get_trailer(scene, response.url)
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['url'] = self.format_link(response, scene.xpath('.//h2/a/@href').get())
            item['type'] = "Scene"
            
            yield self.check_item(item, self.days)


