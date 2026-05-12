import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


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
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = ''

            if image:
                externalid = re.search(r'.*/(\d+)_t\.jpg', item['image'])
                if externalid:
                    item['id'] = externalid.group(1)

            item['url'] = response.url

            item['site'] = "Cum Eating Cuckolds"
            item['parent'] = "Cum Eating Cuckolds"
            item['network'] = "Cum Eating Cuckolds"

            yield self.check_item(item, self.days)