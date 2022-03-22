import re
from datetime import date, timedelta
import string
import base64
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from tpdb.helpers.http import Http


class SiteCumEatingCuckoldsSpider(BaseSceneScraper):
    name = 'CumEatingCuckolds'

    start_urls = [
        'https://www.cumeatingcuckolds.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': '/guest/scenes/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_thumbs"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./p/a/strong/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = ''

            scenedate = scene.xpath('./p/strong[contains(text(), "Date")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = scenedate.replace("st", "").replace("nd", "").replace("rd", "").replace("th", "")
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate)
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%b %d, %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            item['description'] = ''

            performers = scene.xpath('./p/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            item['tags'] = ['Female Domination', 'Cuckold']

            image = scene.xpath('./a/img/@src').get()
            if image:
                item['image'] = image.strip().replace(" ", "%20")
                item['image_blob'] = self.get_image_blob(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None

            item['trailer'] = ''

            if image:
                externalid = re.search(r'.*/(\d+)_t\.jpg', item['image'])
                if externalid:
                    item['id'] = externalid.group(1)

            item['url'] = response.url

            item['site'] = "Cum Eating Cuckolds"
            item['parent'] = "Cum Eating Cuckolds"
            item['network'] = "Cum Eating Cuckolds"

            if item['id'] and item['date'] and "Pics: " not in item['description']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item

    def get_image_blob(self, image):
        if image:
            req = Http.get(image, headers=self.headers, cookies=self.cookies)
            if req and req.ok:
                return base64.b64encode(req.content).decode('utf-8')
        return None
