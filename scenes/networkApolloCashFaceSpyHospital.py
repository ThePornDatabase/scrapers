import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkApolloCashSpyHospitalSpider(BaseSceneScraper):
    name = 'ApolloCashSpyHospital'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.spyhospital.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=1&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('./text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('./following-sibling::span[1]/text()')
            if description:
                description = description.getall()
                description = "".join(description)
                item['description'] = self.cleanup_description(description.strip())

            tags = scene.xpath('./following-sibling::table//span[contains(text(), "Tags:")]/following-sibling::a/text()')
            if tags:
                tags = tags.getall()
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

            image = scene.xpath('./following-sibling::table//th[@align="left"]/a/img/@src')
            if not image:
                image = scene.xpath('./following-sibling::table//img[contains(@src, "SpyHospital.com")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_free', item['image']).group(1)
                if ".com" in item['id'].lower():
                    item['id'] = re.search(r'\.com_(.*)', item['id'].lower()).group(1)
                    scenedate = re.search(r'(\d{6,8})', item['id'])
                    if scenedate:
                        scenedate = scenedate.group(1)
                        item['date'] = self.parse_date(scenedate, date_formats=['%Y%m%d','%y%m%d']).strftime('%Y-%m-%d')

            duration = scene.xpath('./following-sibling::table//text()[contains(., "Duration")]')
            if duration:
                duration = duration.getall()
                duration = "".join(duration)
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    item['duration'] = self.duration_to_seconds(duration.group(1))

            item['site'] = "Spy Hospital"
            item['parent'] = "Spy Hospital"
            item['network'] = "Apollo Cash"
            item['url'] = response.url

            yield item
