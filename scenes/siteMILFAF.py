import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMILFAFSpider(BaseSceneScraper):
    name = 'MILFAF'
    network = 'TugPass'
    parent = 'MILF AF'
    site = 'MILF AF'

    start_urls = [
        'https://www.milfaf.com',
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
        'pagination': '/videos/%s.php',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update-box"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('./div/h3/text()').get())
            item['description'] = scene.xpath('./div/p/text()').get()

            scenedate = scene.xpath('.//span[contains(text(), "Date:")]/text()')
            if scenedate:
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate.get())
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%B %d, %Y']).isoformat()
            if not scenedate:
                item['date'] = self.parse_date('today').isoformat()

            duration = scene.xpath('.//span[contains(text(), "Video")]/text()')
            if duration:
                duration = re.search(r'(\d{1,2}:\d{1,2}:?\d{1,2}?)', duration.get())
                if duration:
                    item['duration'] = self.duration_to_seconds(duration.group(1))
            if not duration:
                item['duration'] = None

            item['performers'] = scene.xpath('./div//a[contains(@href, "/models/")]/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            item['image'] = self.format_link(response, scene.xpath('./div/a/img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = re.search(r'(.*/)', item['image']).group(1)
            item['trailer'] = item['trailer'] + "preview.mp4"

            sceneurl = scene.xpath('./div/a/@href').get()
            if "?nats=" in sceneurl:
                sceneurl = self.format_link(response, re.search(r'(.*)\?nats=', sceneurl).group(1))
            item['tags'] = ['MILF']

            item['url'] = sceneurl
            item['id'] = re.search(r'.*/(.*?)\.htm', sceneurl).group(1)

            item['site'] = "MILF AF"
            item['parent'] = "MILF AF"
            item['network'] = "TugPass"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
