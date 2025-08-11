import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLeilaniLeiSpider(BaseSceneScraper):
    name = 'LeilaniLei'
    network = 'Leilani Lei'
    parent = 'Leilani Lei'
    site = 'Leilani Lei'

    start_urls = [
        'https://leilanilei.elxcomplete.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h4/a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            performers = scene.xpath('.//span[contains(@class, "tour_update_models")]/a/text()')
            if performers:
                item['performers'] = performers.getall()

            scenedate = scene.xpath('.//span[contains(text(), "/20")]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            image = scene.xpath('.//img/@src0_4x')
            if image:
                image = "https://leilanilei.elxcomplete.com" + image.get()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

            sceneid = scene.xpath('.//img[contains(@id, "target")]/@id')
            if sceneid:
                sceneid = re.search(r'(\d+)', sceneid.get())
                if sceneid:
                    item['id'] = sceneid.group(1)

            item['site'] = 'Leilani Lei'
            item['parent'] = 'Leilani Lei'
            item['network'] = 'Leilani Lei'

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
