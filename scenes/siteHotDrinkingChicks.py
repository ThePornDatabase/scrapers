import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotDrinkingChicksSpider(BaseSceneScraper):
    name = 'HotDrinkingChicks'
    network = 'Hot Drinking Chicks'
    parent = 'Hot Drinking Chicks'
    site = 'Hot Drinking Chicks'

    start_urls = [
        'https://www.hdcprojects.com',
    ]

    selector_map = {
        'title': './/h2/a/text()',
        'description': './/div[contains(@class, "custom_text")]/p/text()',
        'date': './/i[contains(@class, "calendar")]/following-sibling::span/text()',
        'image': './/div[contains(@class, "init-video")]/@data-attributes',
        're_image': r'poster\":\"(http.*?)\"',
        'performers': '',
        'tags': '',
        'duration': './/span[contains(@class, "fa5-text") and contains(text(), "inutes")]/text()',
        're_duration': r'(\d{1,2}:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="collection"]')
        for scene in scenes:
            item = SceneItem()
            item['site'] = "Hot Drinking Chicks"
            item['parent'] = "Hot Drinking Chicks"
            item['network'] = "Hot Drinking Chicks"
            item['type'] = "Scene"

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            item['image'] = self.get_image(scene)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['duration'] = self.get_duration(scene)
            item['performers'] = self.get_performers(scene)
            item['tags'] = ['Drinking']
            item['trailer'] = None
            link = scene.xpath('.//h2/a/@href').get()
            item['url'] = self.format_link(response, link)
            item['id'] = re.search(r'.*/(.*)', item['url']).group(1)
            yield self.check_item(item, self.days)

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = response.xpath(self.get_selector_map('image'))
            if image:
                image = image.get()
                image = re.search(self.get_selector_map('re_image'), image).group(1)
                image = image.replace(' ', '%20')
                return image
        return ''
