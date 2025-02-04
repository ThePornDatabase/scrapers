import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SexMexSpider(BaseSceneScraper):
    name = 'SexMex'
    network = 'SexMex'
    parent = 'SexMex'
    site = 'SexMex'

    start_urls = [
        'https://sexmex.xxx/'
        'https://exposedlatinas.com'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videothumbnail"]')
        for scene in scenes:
            item = SceneItem()

            date = scene.xpath('.//p[@class="scene-date"]/text()')
            if date:
                date = date.get()
                date = self.parse_date(date.strip()).strftime('%Y-%m-%d')
            else:
                date = None
            title = scene.xpath('.//h5/a/text()').get()
            title = title.title()
            if " . " in title:
                title = re.search(r'^(.*) \. ', title).group(1).strip()
            description = scene.xpath('.//p[contains(@class,"scene-descr")]/text()').get()
            image = scene.xpath('.//img/@src').get()
            image = image.replace(" ", "%20")
            if "transform.php" in image or "url=" in image:
                image = re.search(r'url=(.*)', image).group(1)
            performers = scene.xpath('.//a[contains(@class, "modelnamesut") and contains(@href, "/models/")]/text()').getall()

            sceneid = scene.xpath('./../@data-setid').get()

            scene = scene.xpath('./a[1]/@href').get()

            item['title'] = title
            item['date'] = date
            item['description'] = description
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['performers'] = performers
            item['tags'] = ['Latina', 'South American']
            item['id'] = sceneid
            item['type'] = 'Scene'
            item['trailer'] = ''
            if "exposedlatinas" in response.url:
                item['site'] = 'Exposed Latinas'
            else:
                item['site'] = 'SexMex'
            item['parent'] = 'SexMex'
            item['network'] = 'SexMex'
            item['url'] = scene

            yield self.check_item(item, self.days)
