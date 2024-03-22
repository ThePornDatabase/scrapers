import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBratPrincessSpider(BaseSceneScraper):
    name = 'BratPrincess'
    site = 'Brat Princess'
    parent = 'Brat Princess'
    network = 'Brat Princess'

    start_urls = [
        'https://www.bratprincess.us',
    ]

    selector_map = {
        'title': './/h6/text()',
        'description': './following-sibling::img[1]/following-sibling::div[contains(@class, "summary")]//p/text()',
        'date': '',
        'image': './following-sibling::div[contains(@class, "poster")]//img/@src',
        'performers': '',
        'tags': '',
        'duration': './following-sibling::div[contains(@class, "runtime")]/div[not(contains(text(), "Runtime"))]/div/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/video-list?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "field-name-title")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = ""
            item['image'] = self.format_link(response, scene.xpath('./following-sibling::div[contains(@class, "poster")]//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = []
            item['tags'] = ['Female Domination', 'Domination']
            item['id'] = slugify.slugify(item['title'])
            item['trailer'] = ""
            item['duration'] = self.get_duration(scene)
            sceneurl = scene.xpath('./following-sibling::div[contains(@class, "links")]//a[contains(@href, "gallery")]/@href').get()
            if sceneurl:
                item['url'] = self.format_link(response, sceneurl)
            else:
                item['url'] = f"https://www.bratprincess.us/gallery-view-videos/{item['id']}"
            item['network'] = self.network
            item['parent'] = self.parent
            item['site'] = self.site
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
