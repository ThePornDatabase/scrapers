import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTiedInPublicSpider(BaseSceneScraper):
    name = 'TiedInPublic'
    network = 'Tied In Public'
    parent = 'Tied In Public'
    site = 'Tied In Public'

    start_urls = [
        'https://www.tiedinpublic.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/collections/page/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="collection"]')
        for scene in scenes:
            item = self.init_scene()
        
            title = scene.xpath('.//h2/a/text()').get()
            item['title'] = self.cleanup_title(title)

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::span[1]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%y-%m-%d']).strftime('%Y-%m-%d')
            
            if self.check_item(item, self.days):

                duration = scene.xpath('.//i[contains(@class, "fa-image")]/following-sibling::span[1]/text()[contains(., "inute")]')
                if duration:
                    duration = duration.get().strip()
                    duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                    if duration:
                        duration = duration.group(1)
                        item['duration'] = self.duration_to_seconds(duration)

                image = scene.xpath('.//div[@class="preview-theme"]/div[@class="row"][1]//a/@href')
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['tags'] = ['Bondage', 'Public', 'Outdoor', 'Public Bondage']

                sceneid = scene.xpath('./@id').get()
                if sceneid:
                    item['id'] = re.search(r'_(\d+)', sceneid).group(1)

                item['url'] = self.format_link(response, scene.xpath('.//h2/a/@href').get())

                item['site'] = 'Tied In Public'
                item['parent'] = 'Tied In Public'
                item['network'] = 'Tied In Public'

                yield item
                
